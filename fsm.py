import random, itertools

class fsm(object):
    '''
    a simplistic implementation of a finite state machine

    example of a fsm that accepts only even words in the alphabet {0, 1}:

    >>> f = fsm(['0', '1'], 2, [0])
    >>> f.add_transitions(0, {'0' : 1, '1' : 1})
    >>> f.add_transitions(1, {'0' : 0, '1' : 0})
    >>> f.process('0')
    False
    >>> f.process('01')
    True
    '''
    def __init__(self, ab, states, accepting):
        self.ab = ab
        self.states = [None]*states
        self.accepting = set(accepting)

    def add_transitions(self, state, edges):
        '''add the given edges as transitions to the given state.

        edges is a dict mapping a letter in the alphabet to its destination
        state
        '''
        if len(edges) != len(self.ab):
            raise ValueError('missing transitions for letters %s' % ', '.join(set(self.ab) - set(edges.keys())))

        for e in edges.keys():
            if e not in self.ab:
                raise ValueError('invalid letter %r in transition' % e)

        # edges is a dict of letters in ab to state numbers
        self.states[state] = edges

    def process(self, word):
        for w in word:
            if w not in self.ab:
                raise ValueError('invalid letter %r in word %r' % (w, word))

        state = self.states[0]
        for w in word:
            next = state[w]
            state = self.states[next]

        return next in self.accepting

    def dot(self, path):
        template = '''digraph fsm {

\trankdir=LR;
\tsize="8,5"

\tnode [shape = doublecircle]; %(accepting)s;
\tnode [shape = point ]; qi

\tnode [shape = circle];
\tqi -> q0;

\t%(transitions)s
}
    '''

        accepting = ' '.join(['q' + str(i) for i in self.accepting])
        transitions = []
        for i, d in enumerate(self.states):
            inverse = {}
            for k, v in d.iteritems():
                inverse.setdefault(v, []).append(k)
            for k, v in sorted(inverse.iteritems()):
                s = 'q%d -> q%d [ label = "%s" ];' % (i, k, ','.join(sorted(v)))
                transitions.append(s)
            transitions.append('')
        transitions = '\n\t'.join(transitions)
        s = template % {'accepting' : accepting, 'transitions' : transitions}
        f = open(path, 'wb')
        f.write(s)
        f.close()
        return s

def fuzzer(fn, fsm, loops, lenskip, tries):
    '''
    fuzzy tests a finite state machine by constructing random strings.

    each loop the length of the test word is increased by lenskip. the word is
    constructed by randomly choosing letters from the finite state machine's
    alphabet.

    once a word is constructed, we run each of its permutations (up to tries)
    through fn and fsm and consider it a failure if the results are different.

    parameters:
        fn - a function that accepts a given word and should return the expected
             result (True or False if the word's in the language, accordingly)
        fsm - the finite state machine being tested
        loops - each loop increases the size of the tested word by ``lenskip``
        lenskip - the number of test characters to increase in each loop
        tries - the number of permutations of each word to test
    '''
    ab = fsm.ab
    currlen = 0
    c = 0

    for i in range(loops):
        currlen += lenskip
        letters = ''.join([random.choice(ab) for n in range(currlen)])
        for p in itertools.islice(itertools.permutations(letters, len(letters)), tries):
            w = ''.join(p)
            r1, r2 = bool(fn(w)), fsm.process(w)
            if r1 != r2:
                raise RuntimeError('wrong result for word %r, expected %r got %r' %
                        (w, r1, r2))
            c += 1
            if c % 1000 == 0:
                print 'tested', c, 'words'

    print 'tested a total of %d words' % c
