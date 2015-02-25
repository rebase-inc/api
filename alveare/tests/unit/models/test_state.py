import unittest
from collections import defaultdict
from alveare.common.state import StateMachine, MACHINE_SET

class TestState(unittest.TestCase):

    def test_basic(test):
        time_line = []
        class A(StateMachine):
            def set_state(self, new_state):
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
        MACHINE_SET.process_all_events()

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
            def set_state(self, new_state):
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
            def set_state(self, new_state):
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
        MACHINE_SET.process_all_events()

        test.assertEqual(sequence_diagram['a'], ['wait_for_pong', 'wait_for_ping'])



    def test_bad_initial_state(test):
        def foo():
            pass

        class Z(StateMachine):
            def set_state(self, new_state):
                pass

            def bar(self):
                pass

            def __init__(self):
                StateMachine.__init__(self, foo)

        with test.assertRaises(AttributeError):
            Z()


    def test_bad_new_state(test):
        def foo():
            pass

        class Z(StateMachine):
            def set_state(self, new_state):
                pass

            def bar(self):
                pass

            def __init__(self):
                StateMachine.__init__(self, self.bar)

        z = Z()
        with test.assertRaises(AttributeError):
            z.add_event_transitions('some_event', {
                z.bar: foo
            })

    def test_bad_current_state_in_transition(test):
        def foo():
            pass

        class Z(StateMachine):
            def set_state(self, new_state):
                pass

            def bar(self):
                pass

            def __init__(self):
                StateMachine.__init__(self, self.bar)

        z = Z()
        with test.assertRaises(AttributeError):
            z.add_event_transitions('some_event', {
                foo: z.bar
            })


    def test_bad_event(test):
        class W(StateMachine):

            def __init__(self):
                StateMachine.__init__(self, None)
                self.add_event_transitions('honk', { None: None })

        w = W()

        with test.assertRaises(ValueError):
            w.send('bogus_event')
