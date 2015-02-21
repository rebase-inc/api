from alveare.common.database import DB

class MachineSet(set):
    def process_all_events(self):
        while any([machine.has_events() for machine in self]):
            for machine in self:
                machine.run()

MACHINE_SET = MachineSet()

class StateMachine(object):

    def __init__(self, initial_state):
        self.event_transitions = {}
        self.queue = []
        self.internal_queue = []
        self._current_state = initial_state

        MACHINE_SET.add(self)

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        self._current_state = new_state
        self.set_state(new_state)

    def set_state(self, new_state):
        raise NotImplementedError()
        pass

    def add_event_transitions(self, event_name, transitions):
        self.event_transitions[event_name] = {}
        for from_state, to_state in transitions.items():
            self.event_transitions[event_name][from_state] = to_state

    def send_event(self, event, *args, **kwargs):
        self.queue.append((event, args, kwargs))

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
            event, args, kwargs = self.get_event()
            try:
                state_action = self.event_transitions[event][self.current_state]
            except KeyError as e:
                raise Exception('No transition from {} via {}'.format(self.current_state, event))
            self.current_state = state_action
            state_action(*args, **kwargs)

class StateModel(DB.String):
    pass

