import sys

class BefungeInterpreter:
    def __init__(self, code):
        self.grid = [list(line.ljust(80)[:80]) for line in code.splitlines()[:25]]
        while len(self.grid) < 25:
            self.grid.append([' '] * 80)
        self.stack = []
        self.pc = [0, 0]  # y, x
        self.delta = [0, 1]  # dy, dx (moving right)
        self.output = []
        self.halt = False
        self.string_mode = False

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        return self.stack.pop() if self.stack else 0

    def advance(self):
        self.pc[0] = (self.pc[0] + self.delta[0]) % 25
        self.pc[1] = (self.pc[1] + self.delta[1]) % 80

    def run(self, max_steps=100000):
        import random
        steps = 0
        while not self.halt and steps < max_steps:
            steps += 1
            y, x = self.pc
            char = self.grid[y][x]

            if self.string_mode:
                if char == '"':
                    self.string_mode = False
                else:
                    self.push(ord(char))
                self.advance()
                continue

            if char == '>':
                self.delta = [0, 1]
            elif char == '<':
                self.delta = [0, -1]
            elif char == 'v':
                self.delta = [1, 0]
            elif char == '^':
                self.delta = [-1, 0]
            elif char == '?':
                self.delta = random.choice([[0,1],[0,-1],[1,0],[-1,0]])
            elif char == '+':
                a, b = self.pop(), self.pop()
                self.push(b + a)
            elif char == '-':
                a, b = self.pop(), self.pop()
                self.push(b - a)
            elif char == '*':
                a, b = self.pop(), self.pop()
                self.push(b * a)
            elif char == '/':
                a, b = self.pop(), self.pop()
                self.push(b // a if a != 0 else 0)
            elif char == '%':
                a, b = self.pop(), self.pop()
                self.push(b % a if a != 0 else 0)
            elif char == '!':
                self.push(1 if self.pop() == 0 else 0)
            elif char == '`':
                a, b = self.pop(), self.pop()
                self.push(1 if b > a else 0)
            elif char == '_':
                val = self.pop()
                self.delta = [0, -1] if val != 0 else [0, 1]
            elif char == '|':
                val = self.pop()
                self.delta = [-1, 0] if val != 0 else [1, 0]
            elif char == '#':
                self.advance()  # skip one cell
            elif char == '@':
                self.halt = True
                break
            elif char == '.':
                self.output.append(str(self.pop()))
            elif char == ',':
                self.output.append(chr(self.pop()))
            elif char == '&':
                self.push(int(input()))
            elif char == '~':
                ch = sys.stdin.read(1)
                self.push(ord(ch) if ch else -1)
            elif char == ':':
                val = self.pop()
                self.push(val)
                self.push(val)
            elif char == '\\':
                a, b = self.pop(), self.pop()
                self.push(a)
                self.push(b)
            elif char == '$':
                self.pop()
            elif char == 'g':
                gy = self.pop()
                gx = self.pop()
                if 0 <= gy < 25 and 0 <= gx < 80:
                    self.push(ord(self.grid[gy][gx]))
                else:
                    self.push(0)
            elif char == 'p':
                gy = self.pop()
                gx = self.pop()
                gv = self.pop()
                if 0 <= gy < 25 and 0 <= gx < 80:
                    self.grid[gy][gx] = chr(gv)
            elif char == '"':
                self.string_mode = True
            elif char.isdigit():
                self.push(int(char))
            # space and unknown chars are no-ops

            self.advance()

        if steps >= max_steps:
            return None  # infinite loop detected
        return "".join(self.output)


def verify(filepath, expected="Hello World"):
    with open(filepath, 'r') as f:
        code = f.read()

    print(f"--- Verifying {filepath} ---")
    interp = BefungeInterpreter(code)
    result = interp.run()

    if result is None:
        print(f"ERROR: Exceeded max steps (probable infinite loop)")
        print(f"   Last IP position: ({interp.pc[1]}, {interp.pc[0]})")
        print(f"   Partial output: '{''.join(interp.output)}'")
        return False
    elif result == expected:
        print(f"PASS: Output matches '{expected}'")
        return True
    else:
        print(f"FAIL: Expected '{expected}', got '{result}'")
        return False


if __name__ == "__main__":
    verify(sys.argv[1])