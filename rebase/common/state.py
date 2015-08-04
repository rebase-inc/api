import copy
from contextlib import ContextDecorator

class Machines(set):
    def process_all_events(self):
        while any([machine.has_events() for machine in self]):
            copy_self = copy.copy(self)
            for machine in copy_self:
                machine.run()

class StateMachine(object):
    machine_pool = None

    def validate_state(self, state):
        state_name = getattr(state, '__name__') # not a method
        getattr(self, state_name) # not in self object

    def __init__(self, initial_state=None):
        self.event_transitions = {}
        self.queue = []
        self.internal_queue = []
        if initial_state:
            self.validate_state(initial_state)
        self._current_state = initial_state

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, new_state):
        self._current_state = new_state
        self.set_state(self._current_state, new_state)

    def set_state(self, old_state, new_state):
        '''
        Provide an implementation in a derived class if you wish to track each state transition

        Params:
        old_state:  the previous current state when the event was received
        new_state:  the new current state (i.e. the value returned by 'self.current_state')

        Note that 'set_state' is called right before the call to the new_state method is made
        '''
        pass

    def add_event_transitions(self, event_name, transitions):
        '''
        Add all possible state transitions for an event.

        Params:
        event_name:     name of one event, string
        transitions:    dictionary of { current_state: new_state }

        'current_state' can be None, in which case the event transition is describing a creation event,
        or must be a method provided by the StateMachine object or a derived child.

        'new_state' can never be None and must be a method provided by the StateMachine object or
        a derived child.

        If the pre-conditions for 'current_state' or 'new_state' are not met, an AttributeError exception will be raised.
        '''

        self.event_transitions[event_name] = {}
        for from_state, to_state in transitions.items():
            # None is a valid from_state
            if from_state:
                self.validate_state(from_state)
            self.validate_state(to_state)
            self.event_transitions[event_name][from_state] = to_state

    def send(self, event, *args, **kwargs):
        '''
        send is used for communications between state machines.

        Params:
        event:          a string whose value has been declared by a call to add_event_transitions.
        args, kwargs:   a generic function signature

        If event has not been declared via a call add_event_transitions, send will raise a ValueError exception
        '''

        if event not in self.event_transitions.keys():
            raise ValueError('Unknown event "{}" sent to {}'.format(event, str(self)))

        if isinstance(self.machine_pool, Machines):
            self.machine_pool.add(self)
        else:
            raise AttributeError('This event cannot be processed outside valid a ManagedState context')
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


class ManagedState(ContextDecorator):
    def __init__(self, name=''):
        self.name = name
        self.pool = Machines()

    def __enter__(self):
        StateMachine.machine_pool = self.pool

    def __exit__(self, exc_type, exc, exc_tb):
        StateMachine.machine_pool.process_all_events()
        StateMachine.machine_pool = None

