
class MachineSet(set):
    def process_all_events(self):
        while any([machine.has_events() for machine in self]):
            for machine in self:
                machine.run()

MACHINE_SET = MachineSet()

class StateMachine(object):

    def validate_state(self, state):
        if not state:
            return # None is a valid state
        # anything else should be a method of this object
        state_name = getattr(state, '__name__') # not a method
        getattr(self, state_name) # not in self object

    def __init__(self, initial_state=None):
        self.event_transitions = {}
        self.queue = []
        self.internal_queue = []
        self._current_state = initial_state
        self.validate_state(initial_state)

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

    def add_event_transitions(self, event_name, transitions):
        '''
        Add all possible state transitions for an event.

        Params:
        event_name:     name of one event, string
        transitions:    dictionary of { current_state: new_state }

        Note that 'current_state' and 'new_state' must be methods provided by the 
        StateMachine object, usually by a class deriving from StateMachine.
        If not, an AttributeError exception will be raised.
        '''
        self.event_transitions[event_name] = {}
        for from_state, to_state in transitions.items():
            self.validate_state(from_state)
            self.validate_state(to_state)
            self.event_transitions[event_name][from_state] = to_state

    def send(self, event, *args, **kwargs):
        if event not in self.event_transitions.keys():
            raise ValueError('Unknown event "{}" sent to {}',format(event, str(self)))
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

