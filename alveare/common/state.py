from alveare.common.database import DB

class StateMachine(object):

    def __init__(self, resume_state=None):
        self.events = {}
        self.queue = []
        self.internal_queue = []
        RUNNER.add_machine(self)

        if resume_state:
            self.current_state = resume_state
        else:
            self.current_state = None
            self.internal_queue.append(('initialize', None))

    def add_event_transitions(self, name, transitions):
        self.events[name] = {}
        for current_state, new_state in transitions.items():
            self.events[name][current_state] = new_state

    def send_event(self, event, data=None):
        self.queue.append((event, data))

    def has_events(self):
        return any([self.queue, self.internal_queue])

    def get_event(self):
        if self.internal_queue:
            return self.internal_queue.pop(0)
        if self.queue:
            return self.queue.pop(0)
        raise NoMoreEvents

    def run(self):
        while self.has_events():
            event, data = self.get_event()
            try:
                new_state = self.events[event][self.current_state]
            except KeyError as e:
                raise Exception('No transition from {} via {}'.format(self.current_state, event))
            new_state()
            self.current_state = new_state

class StateModel(DB.String):
    pass

class Runner(object):
    def __init__(self):
        self.machines = []
        pass

    def add_machine(self, machine):
        self.machines.append(machine)

    def __call__(self):
        while any([machine.has_events() for machine in self.machines]):
            for machine in self.machines:
                machine.run()

RUNNER = Runner()

