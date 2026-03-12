"""
Malbolge "Hello World" generator - FIXED char_for_op.

Key formula: instruction = (mem[C] + C) % 94
We need to find char ch (ASCII 33-126) at position pos such that:
  (ch + pos) % 94 == desired_op

ch ≡ (op - pos) mod 94
r = ((op - pos) % 94 + 94) % 94  (r in [0, 93])
ch = r + 94 if r < 33 else r     (ch in [33, 126])

There's always exactly one valid ch since [33,126] spans 94 values.
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
    """Find the unique ASCII char ch in [33,126] such that (ch + pos) % 94 == op."""
    r = ((op - pos) % 94 + 94) % 94
    ch = r + 94 if r < 33 else r
    # Verify
    assert 33 <= ch <= 126, f"ch={ch} out of range for op={op}, pos={pos}"
    assert (ch + pos) % 94 == op, f"Verification failed: ({ch}+{pos})%94={((ch+pos)%94)} != {op}"
    return ch

# Quick validation
for pos in range(20):
    for op in OPS_VALID:
        ch = char_for_op(op, pos)
        assert (ch + pos) % 94 == op

print("char_for_op validation passed!")

# Now build the program with BFS per character
from collections import deque

def generate_hello_world():
    target = "Hello World"
    
    program_chars = []
    current_A = 0
    current_pos = 0
    
    for target_char in target:
        target_ascii = ord(target_char)
        
        # BFS: find shortest sequence of ops that changes A so A%256 == target_ascii
        # then outputs it
        # State: (A_value, offset_from_current_pos)
        
        queue = deque()
        queue.append((current_A, 0, []))
        visited = {}  # (A, offset) -> True
        visited[(current_A, 0)] = True
        
        found_path = None
        max_depth = 40
        
        while queue:
            A, offset, ops = queue.popleft()
            
            if len(ops) > max_depth:
                continue
            
            pos = current_pos + offset
            
            # Can we output here?
            if A % 256 == target_ascii:
                ch_out = char_for_op(5, pos)
                found_path = ops + [(5, ch_out)]
                break
            
            # Try rotr (39)
            ch = char_for_op(39, pos)
            new_A = rotate(ch)
            state = (new_A, offset + 1)
            if state not in visited:
                visited[state] = True
                queue.append((new_A, offset + 1, ops + [(39, ch)]))
            
            # Try crz (62) 
            ch = char_for_op(62, pos)
            new_A = crazy(A, ch)
            state = (new_A, offset + 1)
            if state not in visited:
                visited[state] = True
                queue.append((new_A, offset + 1, ops + [(62, ch)]))
            
            # Try nop (68)
            state = (A, offset + 1)
            if state not in visited:
                visited[state] = True
                ch = char_for_op(68, pos)
                queue.append((A, offset + 1, ops + [(68, ch)]))
        
        if found_path is None:
            print(f"ERROR: Could not find path to output '{target_char}' (ASCII {target_ascii})")
            print(f"  Current A={current_A}, pos={current_pos}")
            return None
        
        print(f"  '{target_char}' (ASCII {target_ascii}): {len(found_path)} ops starting at pos {current_pos}")
        
        # Apply the path
        for op, ch in found_path:
            program_chars.append(ch)
            if op == 39:  # rotr
                current_A = rotate(ch)
            elif op == 62:  # crz
                current_A = crazy(current_A, ch)
            elif op == 5:  # out
                pass
            elif op == 68:  # nop
                pass
            current_pos += 1
    
    # Add end instruction
    ch_end = char_for_op(81, current_pos)
    program_chars.append(ch_end)
    
    return ''.join(chr(c) for c in program_chars)


result = generate_hello_world()

if result:
    print(f"\nGenerated program ({len(result)} chars):")
    print(repr(result))
    print(f"Bytes: {[ord(c) for c in result]}")
    
    # Verify each char
    for i, c in enumerate(result):
        op = (ord(c) + i) % 94
        valid = op in OPS_VALID
        print(f"  pos {i}: '{c}' (ASCII {ord(c)}), op = {op} {'✓' if valid else '✗ INVALID'}")
    
    # Run through interpreter
    from malbolge import eval as malbolge_eval
    try:
        output = malbolge_eval(result)
        print(f"\nInterpreter output: '{output}'")
        if output.strip() == "Hello World":
            print("SUCCESS!")
        else:
            print(f"MISMATCH: got '{output}', expected 'Hello World'")
    except SystemExit:
        print("\nInterpreter exited with error")
    except Exception as e:
        print(f"\nError: {e}")
else:
    print("\nFailed to generate program")
