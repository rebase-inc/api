import unittest
from collections import defaultdict
from alveare.common.state import StateMachine, MACHINES

class TestState(unittest.TestCase):
    def setUp(self):
        MACHINES.clear()

    def test_basic(test):
        time_line = []
        class A(StateMachine):
            def set_state(self, old_state, new_state):
                time_line.append(new_state.__name__)

            def ping(self):
                test.assertEqual(self._current_state, self.ping)

            def pong(self):
                test.assertEqual(self._current_state, self.pong)

            def __init__(self):
                StateMachine.__init__(self, self.ping)
                self.add_event_transitions('pong', {self.ping: self.pong})
                self.add_event_transitions('ping', {self.pong: self.ping})

        fsm = A()
        fsm.send('pong')
        fsm.send('ping')
        fsm.send('pong')
        fsm.send('ping')
        fsm.send('pong')
        MACHINES.process_all_events()

        test.assertEqual(time_line, ['pong', 'ping', 'pong', 'ping', 'pong'])


    def test_pair(test):
        sequence_diagram = defaultdict(list)

        class A(StateMachine):
            '''
                                         +---------+ 
             +----------+                | Waiting | 
             | Waiting  |<-------pong----+ For     | 
             | For      |                | Pong    | 
             | Ping     +-------ping---->|         | 
             |          |                |         | 
             +----------+                +---------+ 
            '''
            def set_state(self, old_state, new_state):
                sequence_diagram[self.name].append(new_state.__name__)

            def wait_for_ping(self):
                ''' 
                    Wait for an external client to send a 'ping' event to A
                '''
                pass

            def wait_for_pong(self, b):
                b.send('ping', a)

            def __init__(self, name):
                self.name = name
                StateMachine.__init__(self, self.wait_for_ping)
                self.add_event_transitions('ping', {
                    self.wait_for_ping:  self.wait_for_pong
                })
                self.add_event_transitions('pong', {
                    self.wait_for_pong:  self.wait_for_ping
                })

        class B(StateMachine):
            '''
                     +---------+
                     |         |
                  +--+-----+   |
                  |  Wait  |   |
                  |  For   <---+
                  |  Ping  |    
                  +--------+    
            '''
            def set_state(self, old_state, new_state):
                sequence_diagram[self.name].append(new_state.__name__)

            def wait_for_ping(self, a):
                a.send('pong')

            def __init__(self, name):
                self.name = name
                StateMachine.__init__(self, self.wait_for_ping)
                self.add_event_transitions('ping', {
                    self.wait_for_ping:  self.wait_for_ping
                })

        a = A('a')
        b = B('b')
        a.send('ping', b)
        MACHINES.process_all_events()

        test.assertEqual(sequence_diagram['a'], ['wait_for_pong', 'wait_for_ping'])



    def test_bad_initial_state(test):
        def foo():
            pass

        class Z(StateMachine):
            def __init__(self):
                StateMachine.__init__(self, foo)

        with test.assertRaises(AttributeError):
            Z()


    def test_bad_new_state(test):
        def foo():
            pass

        class Z(StateMachine):
            def __init__(self):
                StateMachine.__init__(self)

        z = Z()
        with test.assertRaises(AttributeError):
            z.add_event_transitions('some_event', {
                None: foo
            })

    def test_bad_current_state_in_transition(test):
        def foo():
            pass

        class Z(StateMachine):
            def __init__(self):
                StateMachine.__init__(self)

            def bar(self):
                pass

        z = Z()
        with test.assertRaises(AttributeError):
            z.add_event_transitions('some_event', {
                foo: z.bar
            })


    def test_bad_event(test):

        class W(StateMachine):
            def __init__(self):
                StateMachine.__init__(self)

        w = W()

        with test.assertRaises(ValueError):
            w.send('bogus_event')

    def test_machine_creates_machine(test):
        class A(StateMachine):
            limit = 10
            def __init__(self):
                StateMachine.__init__(self, self.create)
                self.add_event_transitions('create', { self.create: self.create })

            def create(self, counter):
                a_prime = A()
                if counter < A.limit:
                    a_prime.send('create', counter + 1)
        a = A()
        a.send('create', 0)
        MACHINES.process_all_events()

        self.assertEqual(len(MACHINES), 10)

    def test_many_machines(test):
        ring_length = 100 # nodes
        lapses = 10

        class Node(StateMachine):
            def __init__(self):
                StateMachine.__init__(self, self.ping)
                self.next = None
                self.ping_counter = 0
                self.add_event_transitions('ping', { self.ping: self.ping })
                self.add_event_transitions('stop', { self.ping: self.stopped })

            def ping(self):
                self.ping_counter += 1
                if self.ping_counter < lapses:
                    if not self.next:
                        raise AttributeError('Node {} was not initialized with a valid next node'.format(str(self)))
                    self.next.send('ping')
                else:
                    self.send('stop')

            def stopped(self):
                pass

        ring = [ Node() for i in range(ring_length) ]
        first_node = ring[0]
        last_node =  ring[-1]
        for index, node in enumerate(ring):
            if node == last_node:
                last_node.next = first_node
            else:
                node.next = ring[index+1]

        first_node.send('ping')
        MACHINES.process_all_events() # this will trigger (ring_lenth*lapses)-1 events being fired and processed

        test.assertEqual(first_node.current_state, first_node.stopped)
        test.assertEqual(first_node.ping_counter, lapses)
        for node in ring[1:]:
            test.assertEqual(node.current_state, node.ping)
            test.assertEqual(node.ping_counter, lapses-1)

