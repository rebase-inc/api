from copy import copy
from datetime import datetime, timedelta
from functools import partial
from sched import scheduler
from time import sleep

from sqlalchemy import or_

from rebase import create_app
from rebase.common.state import ManagedState
from rebase.models.auction import Auction

_, _, db = create_app()

class Proxy(scheduler):
    def __init__(self):
        self.check_queue_period = timedelta(minutes=1)

    def reset(self, obj):
        self.__dict__.update(copy(obj.__dict__))

    def check_the_queue(self):
        self.enterabs(
            datetime.now() + self.check_queue_period,
            0,
            lambda : None
        )


def wait(sched, delta):
    if delta == 0:
        return
    if delta > sched.check_queue_period:
        sched.check_the_queue()
    else:
        sleep(delta.total_seconds())


def auction_expires(auction):
    with ManagedState():
        auction.machine.send('fail')
    db.session.commit()

def main():
    mainScheduler = Proxy()
    mainScheduler.reset(
        scheduler(
            timefunc=datetime.now,
            delayfunc=partial(wait, mainScheduler)
        )
    )
    while True:
        active_auctions = Auction.query.filter(or_(Auction.state=='waiting_for_bids', Auction.state=='created')).all()
        for auction in active_auctions:
            mainScheduler.enterabs(auction.expires, 0, auction_expires, argument=(auction,))

        mainScheduler.run()
        mainScheduler.check_the_queue()

if __name__ == '__main__':
    main()
