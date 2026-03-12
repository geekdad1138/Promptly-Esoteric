"""
Generate a Malbolge program that prints "Hello World".

Strategy: We build the program one instruction at a time. At each step,
we know the current state (A, C, D, memory) and we know what operation
we need next. We search for a character to place at position C that,
when processed by the interpreter, produces the desired effect.

The key insight: after initialization of the program characters into memory,
the remaining memory is filled with crazy(mem[i-1], mem[i-2]).

Operations and their (mem[c]+c)%94 values:
  4  -> jmp [d]     (j)
  5  -> out a       (<)  - prints chr(a % 256)
  23 -> in a        (i)
  39 -> rotr [d]    (*)  - rotate mem[d] right (ternary), set a = result 
  40 -> mov d, [d]  (p)
  62 -> crz [d], a  (/)  - crazy(a, mem[d]), store in mem[d], set a = result
  68 -> nop         (o)
  81 -> end         (v)

Valid ops: 4, 5, 23, 39, 40, 62, 68, 81

For a character at position C with ASCII value `ch`:
  (ch + C) % 94 = desired_op
  => ch = (desired_op - C) % 94 + 33    (must be in range 33..126)
  But we also need (ch + C) % 94 to be in OPS_VALID

After executing an instruction, mem[C] is encrypted:
  if 33 <= mem[C] <= 126: mem[C] = ENCRYPT[mem[C] - 33]
Then C++, D++.

The encryption table (ENCRYPT):
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
    """Find a printable ASCII char that, when placed at position `pos`,
    gives operation `op` via (char + pos) % 94 == op"""
    ch = (op - pos % 94) % 94 + 33
    if 33 <= ch <= 126:
        return ch
    return None

def try_generate():
    """
    Try to generate Malbolge code for "Hello World".
    
    The approach: We need to manipulate the A register to hold ASCII values
    of each character, then output them. 
    
    In Malbolge, we can use:
    - rotr (op 39): rotates mem[D] right in ternary, sets A = result
    - crz (op 62): crazy(A, mem[D]), stores in mem[D], sets A = result  
    - out (op 5): prints chr(A % 256)
    - mov d, [d] (op 40): D = mem[D], for navigation
    - jmp [d] (op 4): C = mem[D], for jumps
    - nop (op 68): do nothing
    - end (op 81): halt
    
    The simplest approach for "Hello World":
    We need a sequence of operations that sets A to each character's ASCII
    value, then outputs it.
    
    Since after loading the program, remaining memory is filled with 
    crazy(mem[i-1], mem[i-2]), and D increments with C, we need to 
    carefully plan which operations to use.
    
    A simpler greedy approach: use a BFS/simulation to find the right
    sequence of ops. At each step after the program chars, mem is determined
    by the crazy fill, so we can predict what rotr and crz will do to A.
    """
    target = "Hello World"
    
    # We'll try to build a sequence of instructions.
    # After each instruction is placed at position i, the memory at i is set.
    # D starts at 0 and increments with C.
    # On each step, C=D (they start the same and increment together).
    # So mem[D] = mem[C] = the character we placed.
    
    # Wait - C and D both start at 0 and both increment by 1 each step.
    # So D always equals C throughout execution (unless we use mov d,[d] or jmp).
    # That means mem[D] = mem[C] = the instruction character itself.
    
    # After we execute the instruction, mem[C] gets encrypted. Then C++, D++.
    
    # For "out" (op 5): prints chr(A % 256). Doesn't change A.
    # For "rotr" (op 39): A = rotate(mem[D]). mem[D] = rotate(mem[D]).
    #   Since D=C, mem[D] is the character we placed. So A = rotate(char_value).
    # For "crz" (op 62): A = crazy(A, mem[D]). mem[D] = crazy(A, mem[D]).
    #   Since D=C, mem[D] is the character value.
    
    # Strategy: 
    # For each character in "Hello World", we need two instructions:
    # 1. Set A to the right value (via rotr or crz)
    # 2. Output A (via out, op 5)
    
    # Let's think about using rotr:
    # rotr at position i with char ch: A = rotate(ch). 
    # We need rotate(ch) % 256 = target_ascii
    # So we need to find ch such that:
    #   (ch + i) % 94 == 39  (rotr op)
    #   rotate(ch) % 256 == target_char
    
    # rotate(n) = 19683*(n%3) + n//3
    # For printable chars (33-126):
    # rotate(33) = 19683*0 + 11 = 11
    # Let me compute rotate for all printable chars
    
    print("Exploring rotate values for printable ASCII:")
    rotate_map = {}  # desired_A -> list of chars that produce it via rotate
    for ch in range(33, 127):
        r = rotate(ch)
        a_val = r % 256
        if a_val not in rotate_map:
            rotate_map[a_val] = []
        rotate_map[a_val].append(ch)
    
    for char in target:
        asc = ord(char)
        if asc in rotate_map:
            print(f"  '{char}' (ASCII {asc}): can be produced by rotate of chars {rotate_map[asc]}")
        else:
            print(f"  '{char}' (ASCII {asc}): CANNOT be produced by simple rotate")
    
    # This likely won't work for all chars. Let's try a simulation approach.
    # We simulate forward, trying different sequences of operations.
    
    return simulate_and_build(target)

def simulate_and_build(target):
    """
    Build Malbolge code by simulation.
    
    We maintain the full interpreter state and try to find, at each step,
    which operation to perform to eventually output all of "Hello World".
    
    Since C and D both start at 0 and increment together (unless we use
    jmp or mov d,[d]), and we want a linear program, D=C throughout.
    
    Plan: Use DFS/BFS with a bounded search to find a valid program.
    """
    
    # Let's first try the simplest approach: a sequence of (set_A, print) pairs.
    # For setting A, we can use rotr (39) or crz (62).
    # rotr: A = rotate(mem[D]) where mem[D] = char at current position
    # crz: A = crazy(A, mem[D]) where mem[D] = char at current position
    
    # After rotr or crz executes, mem[C] gets encrypted, then C++, D++.
    # On the next step (out), mem[C] is the next char we place.
    
    # For the "out" step, we need (next_char + C) % 94 == 5.
    # The "out" doesn't change A, so we just need the right char.
    
    # So the pattern is: [set_A_char, out_char, set_A_char, out_char, ...]
    
    # For rotr: we need a char `ch` at position `pos` such that:
    #   1. (ch + pos) % 94 == 39
    #   2. rotate(ch) % 256 == target_ascii_value
    #   3. 33 <= ch <= 126
    
    # For crz: we need a char `ch` at position `pos` such that:
    #   1. (ch + pos) % 94 == 62
    #   2. crazy(current_A, ch) % 256 == target_ascii_value
    #   3. 33 <= ch <= 126
    
    program = []
    A = 0
    pos = 0
    
    for char_idx, target_char in enumerate(target):
        target_ascii = ord(target_char)
        found = False
        
        # Try rotr first
        ch_rotr = char_for_op(39, pos)
        if ch_rotr is not None and 33 <= ch_rotr <= 126:
            new_A = rotate(ch_rotr)
            if new_A % 256 == target_ascii:
                program.append(ch_rotr)
                A = new_A
                pos += 1
                # Now place an "out" character
                ch_out = char_for_op(5, pos)
                if ch_out is not None and 33 <= ch_out <= 126:
                    program.append(ch_out)
                    pos += 1
                    found = True
                    print(f"  '{target_char}': rotr({ch_rotr}={chr(ch_rotr)}) -> A={A}, then out at pos {pos-1}")
                else:
                    program.pop()
                    pos -= 1
        
        if not found:
            # Try crz
            ch_crz = char_for_op(62, pos)
            if ch_crz is not None and 33 <= ch_crz <= 126:
                new_A = crazy(A, ch_crz)
                if new_A % 256 == target_ascii:
                    program.append(ch_crz)
                    A = new_A
                    pos += 1
                    ch_out = char_for_op(5, pos)
                    if ch_out is not None and 33 <= ch_out <= 126:
                        program.append(ch_out)
                        pos += 1
                        found = True
                        print(f"  '{target_char}': crz(A, {ch_crz}={chr(ch_crz)}) -> A={A}, then out at pos {pos-1}")
                    else:
                        program.pop()
                        pos -= 1
        
        if not found:
            # Try nop + rotr, or multiple crz operations to reach the target
            print(f"  '{target_char}' (ASCII {target_ascii}): Could not find simple 2-instruction sequence at pos {pos}")
            # Try inserting nops to shift position
            for nops in range(1, 50):
                ch_nop = char_for_op(68, pos)
                if ch_nop is not None and 33 <= ch_nop <= 126:
                    program.append(ch_nop)
                    pos += 1
                    
                    # Try rotr
                    ch_rotr = char_for_op(39, pos)
                    if ch_rotr is not None and 33 <= ch_rotr <= 126:
                        new_A = rotate(ch_rotr)
                        if new_A % 256 == target_ascii:
                            program.append(ch_rotr)
                            A = new_A
                            pos += 1
                            ch_out = char_for_op(5, pos)
                            if ch_out is not None and 33 <= ch_out <= 126:
                                program.append(ch_out)
                                pos += 1
                                found = True
                                print(f"  '{target_char}': {nops} nop(s) + rotr({ch_rotr}) -> A={A}, then out")
                                break
                            else:
                                program.pop()
                                pos -= 1
                    
                    if not found:
                        # Try crz
                        ch_crz = char_for_op(62, pos)
                        if ch_crz is not None and 33 <= ch_crz <= 126:
                            new_A = crazy(A, ch_crz)
                            if new_A % 256 == target_ascii:
                                program.append(ch_crz)
                                A = new_A
                                pos += 1
                                ch_out = char_for_op(5, pos)
                                if ch_out is not None and 33 <= ch_out <= 126:
                                    program.append(ch_out)
                                    pos += 1
                                    found = True
                                    print(f"  '{target_char}': {nops} nop(s) + crz -> A={A}, then out")
                                    break
                                else:
                                    program.pop()
                                    pos -= 1
                else:
                    # Can't place nop here, try another approach
                    break
            
            if not found:
                print(f"  FAILED to find instruction for '{target_char}'")
                return None
    
    # Add end instruction
    ch_end = char_for_op(81, pos)
    if ch_end is not None and 33 <= ch_end <= 126:
        program.append(ch_end)
    else:
        # Try nops before end
        for _ in range(94):
            ch_nop = char_for_op(68, pos)
            if ch_nop is not None:
                program.append(ch_nop)
                pos += 1
            ch_end = char_for_op(81, pos)
            if ch_end is not None and 33 <= ch_end <= 126:
                program.append(ch_end)
                break
    
    return ''.join(chr(c) for c in program)


result = try_generate()
if result:
    print(f"\nGenerated program ({len(result)} chars):")
    print(repr(result))
    
    # Verify with the actual interpreter
    import sys
    sys.path.insert(0, r'C:\Users\dave\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages')
    from malbolge import eval as malbolge_eval
    output = malbolge_eval(result)
    print(f"\nInterpreter output: '{output}'")
    if output.strip() == "Hello World":
        print("SUCCESS!")
    else:
        print("MISMATCH - need to debug")
else:
    print("Failed to generate program")
