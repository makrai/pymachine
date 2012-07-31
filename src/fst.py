from collections import defaultdict
import logging
import re

class FSA:
    def __init__(self, regex_transitions=True):
        self.states = set()
        self.input_alphabet = set()
        self.init_states = set()
        self.final_states = set()
        self.transitions = defaultdict(dict)
        self.active_states = None
        self.regex_transitions = regex_transitions

    def add_state(self, state, is_init=False, is_final=False):
        self.states.add(state)
        if is_init:
            self.set_init(state)
        if is_final:
            self.set_final(state)

    def add_states(self, states):
        for state in states:
            if isinstance(state, tuple) and len(state) == 3:
                self.add_state(*state)
            else:
                raise TypeError("states for FSA.add_states() has to be tuples")

    def set_init(self, state):
        if state not in self.states:
            raise ValueError("state to be init has to be in states already")
        else:
            self.init_states.add(state)

    def set_final(self, state):
        if state not in self.states:
            raise ValueError("state to be final has to be in states already")
        else:
            self.final_states.add(state)

    def add_transition(self, string, input_state, output_state):
        if input_state not in self.states or output_state not in self.states:
            raise ValueError("transition states has to be in states already")
        if self.regex_transitions:
            input_ = re.compile(string)
        else:
            input_ = string
            self.input_alphabet.add(string)
        self.transitions[input_state][input_] = output_state

    def check_states(self):
        if len(self.states) == 0:
            raise Exception("FSA has no states")
        if len(self.init_states) == 0:
            raise Exception("No init states in the FSA")
        if len(self.final_states) == 0:
            raise Exception("No final/acceptor states in the FSA")

    def init_active_states(self):
        self.active_states = set(self.init_states)

    def reset(self):
        self.init_active_states()

    def in_final(self):
        return len(self.active_states & self.final_states) > 0

    def read_symbol(self, string):
        self.check_states()
        if self.active_states is None:
            self.init_active_states()
        new_active_states = set() 
        for active_state in self.active_states:
            if self.regex_transitions:
                for trans_pattern, out_state in (
                        self.transitions[active_state].iteritems()):

                    if trans_pattern.search(string) is not None:
                        new_active_states.add(
                            self.transitions[active_state][trans_pattern])

            else:
                if string in self.transitions[active_state]:
                    new_active_states.add(
                        self.transitions[active_state][string])
        self.active_states = new_active_states

    def read_word(self, word):
        for symbol in word:
            self.read_symbol(symbol)

    def read(self, what):
        if isinstance(what, str):
            return self.read_symbol(what)
        elif isinstance(what, list):
            return self.read_word(what)

class FST(FSA):
    def __init__(self, output_alphabet=None):
        FSA.__init__(self)
        if output_alphabet is None:
            self.output_alphabet = set()
        else:
            self.set_output_aplhabet(output_alphabet)

    def set_output_alphabet(self, a):
        if isinstance(a, set):
            self.output_alphabet = a
        else:
            raise TypeError("output alphabet has to be type of set")

    def add_transition(self, input_string, output_string, input_state,
                       output_state):
        # TODO
        # outputs are strings? what if input was regexp?
        raise Exception("FST.add_transition() has to be implemented.")

    def read_symbol(self, string):
        # TODO
        # deterministic or non-deterministic?
        # output is a print, a function call or what?
        raise Exception("FST.read_symbol() has to be implemented.")
