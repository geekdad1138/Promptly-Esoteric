"""
Malbolge "Hello World" generator - BFS approach, one character at a time.

Key facts:
- C and D both start at 0 and increment by 1 each step (linear program, no jumps)
- So D = C always, and mem[D] = mem[C] = the instruction character
- At each position, the character is determined by the chosen operation
- Only rotr and crz change A; out prints A%256; nop does nothing

Strategy: For each target output character, use BFS to find the shortest 
sequence of rotr/crz/nop instructions from current A to an A where A%256 = target,
then add an out instruction.
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
    """Get the ASCII char needed at position pos to encode operation op."""
    ch = (op - pos % 94) % 94 + 33
    if 33 <= ch <= 126:
        return ch
    return None

def op_available(op, pos):
    """Check if operation op can be encoded at position pos."""
    return char_for_op(op, pos) is not None

def generate_hello_world():
    target = "Hello World"
    
    program_chars = []  # list of ASCII values
    current_A = 0
    current_pos = 0
    
    for target_char in target:
        target_ascii = ord(target_char)
        
        # BFS: find shortest sequence of ops (rotr=39, crz=62, nop=68) 
        # starting from current_pos and current_A,
        # that reaches an A value where A%256 == target_ascii,
        # followed by an out (5) instruction.
        
        from collections import deque
        
        # State: (A_value, position_offset)
        # We search from offset 0 (current_pos)
        # Max search depth
        max_depth = 100
        
        queue = deque()
        queue.append((current_A, 0, []))  # (A, offset, ops_list)
        visited = set()
        visited.add((current_A, 0))
        
        found_path = None
        
        while queue:
            A, offset, ops = queue.popleft()
            
            if len(ops) > max_depth:
                break
            
            pos = current_pos + offset
            
            # Check if we can output at this position  
            if A % 256 == target_ascii and op_available(5, pos):
                found_path = ops + [5]
                break
            
            # Try rotr (39)
            if op_available(39, pos):
                ch = char_for_op(39, pos)
                new_A = rotate(ch)
                state = (new_A, offset + 1)
                if state not in visited:
                    visited.add(state)
                    queue.append((new_A, offset + 1, ops + [39]))
            
            # Try crz (62)
            if op_available(62, pos):
                ch = char_for_op(62, pos)
                new_A = crazy(A, ch)
                state = (new_A, offset + 1)
                if state not in visited:
                    visited.add(state)
                    queue.append((new_A, offset + 1, ops + [62]))
            
            # Try nop (68) - only useful to shift position for different char values
            if op_available(68, pos):
                state = (A, offset + 1)
                if state not in visited:
                    visited.add(state)
                    queue.append((A, offset + 1, ops + [68]))
        
        if found_path is None:
            print(f"ERROR: Could not find path to output '{target_char}' (ASCII {target_ascii})")
            print(f"  Current A={current_A}, pos={current_pos}")
            return None
        
        print(f"  '{target_char}' (ASCII {target_ascii}): {len(found_path)} ops at pos {current_pos}: {found_path}")
        
        # Apply the found path
        for op in found_path:
            ch = char_for_op(op, current_pos)
            program_chars.append(ch)
            
            if op == 39:  # rotr
                current_A = rotate(ch)
            elif op == 62:  # crz
                current_A = crazy(current_A, ch)
            elif op == 5:  # out
                pass  # A unchanged
            elif op == 68:  # nop
                pass
            
            current_pos += 1
    
    # Add end instruction
    end_added = False
    for nops in range(94):
        pos = current_pos + nops
        if op_available(81, pos):
            # Add nops first
            for i in range(nops):
                ch = char_for_op(68, current_pos)
                if ch is None:
                    break
                program_chars.append(ch)
                current_pos += 1
            else:
                ch = char_for_op(81, current_pos)
                program_chars.append(ch)
                end_added = True
                break
    
    if not end_added:
        print("ERROR: Could not add end instruction")
        return None
    
    return ''.join(chr(c) for c in program_chars)


print("Generating Malbolge 'Hello World'...")
result = generate_hello_world()

if result:
    print(f"\nGenerated program ({len(result)} chars):")
    print(repr(result))
    print(f"Raw bytes: {[ord(c) for c in result]}")
    
    # Verify with interpreter
    from malbolge import eval as malbolge_eval
    output = malbolge_eval(result)
    print(f"\nInterpreter output: '{output}'")
    if output.strip() == "Hello World":
        print("SUCCESS!")
        # Save to file
        with open(r"c:\Users\dave\Documents\GitHub\Promptly-Esoteric\experiments\malbolge\01-hello-world\hello.mb", 'w') as f:
            f.write(result)
        print("Saved to hello.mb")
    else:
        print(f"MISMATCH: got '{output}', expected 'Hello World'")
else:
    print("\nFailed to generate program")
