from copy import copy
from datetime import datetime, timedelta
from functools import partial
from logging import getLogger
from multiprocessing import current_process
from sched import scheduler
from signal import signal, SIGINT, SIGTERM, SIGQUIT
from sys import exit
from time import sleep

from sqlalchemy import or_

from rebase.app import create
from rebase.common.state import ManagedState
from rebase.models import (
    Auction,
    Work,
    Mediation,
)


_, _, db = create()


logger = getLogger()


current_process().name = 'scheduler'


def load_new_events(sched):
    for event in sched.queue:
        sched.cancel(event)
    auctions = Auction.query.filter(or_(Auction.state=='waiting_for_bids', Auction.state=='created')).all()
    for auction in auctions:
        sched.enterabs(auction.expires, 0, auction_expired, argument=(auction.id,))

    works = Work.query.filter_by(state='in_progress').all()
    for work in works:
        sched.enterabs(work.offer.bid.auction.finish_work_by, 0, work_expired, argument=(work.id,))

    mediations = Mediation.query.filter(or_(Mediation.state=='waiting_for_client', Mediation.state=='waiting_for_dev')).all()
    for mediation in mediations:
        sched.enterabs(mediation.timeout, 0, mediation_timed_out, argument=(mediation.id,))
    logger.debug('Loaded %d Events in the queue', len(sched.queue))


class Proxy(scheduler):
    check_queue_period = timedelta(minutes=5)

    def reset(self, obj):
        self.__dict__.update(copy(obj.__dict__))

    def check_the_queue(self):
        self.enterabs(
            datetime.now() + self.check_queue_period,
            0,
            partial(load_new_events, self)
        )


def wait(sched, delta):
    if delta == 0:
        return
    if delta > sched.check_queue_period:
        sched.check_the_queue()
    else:
        sleep(delta.total_seconds())


def auction_expired(auction_id):
    auction = Auction.query.get(auction_id)
    if auction and (auction.state == 'waiting_for_bids' or auction.state == 'created'):
        with ManagedState():
            auction.machine.send('fail')
        db.session.commit()
        logger.info('%s has expired now', auction)


def work_expired(work_id):
    work = Work.query.get(work_id)
    if work and work.state == 'in_progress':
        with ManagedState():
            work.machine.send('review')
        db.session.commit()
        logger.info('%s has expired now', work)


def mediation_timed_out(mediation_id):
    mediation = Mediation.query.get(mediation_id)
    if mediation and (mediation.state == 'waiting_for_client' or mediation.state == 'waiting_for_dev'):
        with ManagedState():
            mediation.machine.send('timeout')
        db.session.commit()
        logger.info('%s has expired now', mediation)


def quit(signal_number, frame):
    exit()


def main():
    signal(SIGINT, quit)
    signal(SIGTERM, quit)
    signal(SIGQUIT, quit)
    main_scheduler = Proxy()
    main_scheduler.reset(
        scheduler(
            timefunc=datetime.now,
            delayfunc=partial(wait, main_scheduler)
        )
    )
    load_new_events(main_scheduler)
    while True:
        main_scheduler.run()
        main_scheduler.check_the_queue()


if __name__ == '__main__':
    main()
