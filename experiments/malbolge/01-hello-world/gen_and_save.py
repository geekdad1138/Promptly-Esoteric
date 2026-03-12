"""
Generate and save the Malbolge Hello World program.
"""

TABLE_CRAZY = (
    (1, 0, 0),
    (1, 0, 2),
    (2, 2, 1)
)

ENCRYPT = list(map(ord,
              '5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB'
              '6v^=I_0/8|jsb9m<.TVac`uY*MK\'X~xDl}REokN:#?G\"i@'))

OPS_VALID = (4, 5, 23, 39, 40, 62, 68, 81)
POW9, POW10 = 3**9, 3**10

def rotate(n):
    return POW9 * (n % 3) + n // 3

def crazy(a, b):
    result = 0
    d = 1
    for i in range(10):
        result += TABLE_CRAZY[int((b/d)%3)][int((a/d)%3)] * d
        d *= 3
    return result

def char_for_op(op, pos):
    r = ((op - pos) % 94 + 94) % 94
    ch = r + 94 if r < 33 else r
    assert 33 <= ch <= 126
    assert (ch + pos) % 94 == op
    return ch

def generate_hello_world():
    target = "Hello World"
    from collections import deque
    
    program_chars = []
    current_A = 0
    current_pos = 0
    
    for target_char in target:
        target_ascii = ord(target_char)
        
        queue = deque()
        queue.append((current_A, 0, []))
        visited = set()
        visited.add((current_A, 0))
        
        found_path = None
        
        while queue:
            A, offset, ops = queue.popleft()
            if len(ops) > 50:
                continue
            
            pos = current_pos + offset
            
            if A % 256 == target_ascii:
                ch_out = char_for_op(5, pos)
                found_path = ops + [(5, ch_out)]
                break
            
            # rotr
            ch = char_for_op(39, pos)
            new_A = rotate(ch)
            state = (new_A, offset + 1)
            if state not in visited:
                visited.add(state)
                queue.append((new_A, offset + 1, ops + [(39, ch)]))
            
            # crz
            ch = char_for_op(62, pos)
            new_A = crazy(A, ch)
            state = (new_A, offset + 1)
            if state not in visited:
                visited.add(state)
                queue.append((new_A, offset + 1, ops + [(62, ch)]))
            
            # nop
            state = (A, offset + 1)
            if state not in visited:
                visited.add(state)
                ch = char_for_op(68, pos)
                queue.append((A, offset + 1, ops + [(68, ch)]))
        
        if found_path is None:
            print(f"ERROR: Could not find path for '{target_char}'")
            return None
        
        for op, ch in found_path:
            program_chars.append(ch)
            if op == 39:
                current_A = rotate(ch)
            elif op == 62:
                current_A = crazy(current_A, ch)
            current_pos += 1
    
    # End
    ch_end = char_for_op(81, current_pos)
    program_chars.append(ch_end)
    
    return ''.join(chr(c) for c in program_chars)

result = generate_hello_world()
print(f"Program length: {len(result)}")
print(f"Program repr: {repr(result)}")

# Save to file
output_path = r"c:\Users\dave\Documents\GitHub\Promptly-Esoteric\experiments\malbolge\01-hello-world\hello.mb"
with open(output_path, 'w', newline='') as f:
    f.write(result)
print(f"Saved to {output_path}")

# Verify with interpreter
from malbolge import eval as malbolge_eval
output = malbolge_eval(result)
print(f"Interpreter output: '{output}'")
assert output.strip() == "Hello World", f"MISMATCH: '{output}'"
print("VERIFIED: Output matches 'Hello World'")
