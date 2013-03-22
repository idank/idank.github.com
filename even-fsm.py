import fsm

f = fsm.fsm(['0', '1'], 2, [0])
f.add_transitions(0, {'0' : 1, '1' : 1})
f.add_transitions(1, {'0' : 0, '1' : 0})

def checkword(w):
    return len(w) % 2 == 0

fsm.fuzzer(checkword, f, 1000, 1, 100)
