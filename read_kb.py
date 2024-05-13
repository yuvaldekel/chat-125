import KBHit_py
import select

while True:

    kb = KBHit_py.KBHit()
    string = []
    messages = []
    while True:
        rd, wr ,er = select.select([kb.kbhit()], [], [])
        for r in rd:
            
            c = kb.getch()
            if ord(c) == 10: # ESC
                print("break")
                messages.append(''.join(string))
                string= []
                break
            string.append(c)
            print(c)