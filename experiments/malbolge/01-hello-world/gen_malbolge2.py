"""
Malbolge "Hello World" generator - comprehensive approach.

Key insight: In Malbolge, C and D start at 0 and both increment by 1 
after each instruction (unless jmp or mov_d is used). So D=C always
in a linear program, meaning mem[D] = mem[C] = the instruction character.

After execution of an instruction at position C:
  - mem[C] is encrypted via the ENCRYPT table
  - C += 1, D += 1

For rotr (op 39): A = mem[D] = rotate(mem[D]). Since D=C, this rotates
the instruction char itself and sets A.

For crz (op 62): A = mem[D] = crazy(A, mem[D]). Operates on instruction char.

For out (op 5): prints chr(A % 256). Does not modify A.

Problem: rotate(ch) for ch in 33..126 gives limited values.
We need to chain multiple crz operations to reach desired A values.

Better approach: Use DFS/BFS to find instruction sequences.
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
    """Find a printable ASCII char at position pos that maps to op."""
    ch = (op - pos % 94) % 94 + 33
    if 33 <= ch <= 126:
        return ch
    return None

def search_program(target_str):
    """
    Use BFS to find a sequence of Malbolge operations that prints target_str.
    
    State: (char_index, A_value, position)
    
    At each step, we can use:
    - nop (68): A unchanged, pos += 1
    - rotr (39): A = rotate(char_at_pos), pos += 1
    - crz (62): A = crazy(A, char_at_pos), pos += 1  
    - out (5): print chr(A%256), pos += 1 -- only if A%256 == target[char_index]
    - end (81): halt -- only after all chars printed
    
    For rotr: the char at pos must satisfy (ch + pos)%94 == 39, and ch ∈ [33,126]
      => ch is determined by pos. So A = rotate(ch).
    For crz: ch is determined by pos. So A = crazy(old_A, ch).
    For nop: ch is determined by pos.
    For out: ch is determined by pos.
    
    So at each position, the char is determined by the op we choose!
    The only variable is which op to choose at each position.
    """
    from collections import deque
    
    target = [ord(c) for c in target_str]
    
    # State: (output_index, A_value)
    # Path: list of ops chosen at each position
    # Position is implicit from len(path)
    
    # BFS with states
    # But A_value can be huge (up to 59048)... too many states for BFS
    # Let's use iterative deepening or smarter search
    
    # Actually, let's think about this differently.
    # At each position, the char is fixed given the op choice.
    # The only ops that change A are rotr and crz.
    # out only works when A%256 matches the next target char.
    
    # Let's precompute: for each position, what A values does rotr give?
    # rotr at pos: ch = char_for_op(39, pos), A = rotate(ch)
    # crz at pos: ch = char_for_op(62, pos), A = crazy(old_A, ch)
    
    # The search space is: at each position, choose one of {nop, rotr, crz, out, end}
    # But we can prune: out only when ready, end only after all output done
    
    # Let's try DFS with limited depth
    
    max_pos = 200  # Maximum program length
    
    # Precompute rotr result for each position
    rotr_result = {}
    for pos in range(max_pos):
        ch = char_for_op(39, pos)
        if ch is not None:
            rotr_result[pos] = rotate(ch)
    
    # Precompute crz char for each position
    crz_char = {}
    for pos in range(max_pos):
        ch = char_for_op(62, pos)
        if ch is not None:
            crz_char[pos] = ch
    
    # Check which ops are available at each position
    available = {}
    for pos in range(max_pos):
        ops = []
        for op in OPS_VALID:
            ch = char_for_op(op, pos)
            if ch is not None:
                ops.append(op)
        available[pos] = ops
    
    # DFS
    best_program = [None]
    
    def dfs(pos, A, out_idx, program):
        if best_program[0] is not None:
            return  # Already found a solution
        
        if out_idx == len(target):
            # All characters printed, add end
            if 81 in available.get(pos, []):
                ch = char_for_op(81, pos)
                program.append(ch)
                best_program[0] = program[:]
                program.pop()
            else:
                # Try nops until we can end
                for nop_count in range(94):
                    nop_pos = pos + nop_count
                    if nop_pos >= max_pos:
                        break
                    if nop_count > 0:
                        if 68 not in available.get(nop_pos-1, []):
                            break
                    if 81 in available.get(nop_pos, []):
                        # Add nops then end
                        nops_to_add = []
                        valid = True
                        for np in range(pos, nop_pos):
                            ch_nop = char_for_op(68, np)
                            if ch_nop is None:
                                valid = False
                                break
                            nops_to_add.append(ch_nop)
                        if valid:
                            ch_end = char_for_op(81, nop_pos)
                            program.extend(nops_to_add)
                            program.append(ch_end)
                            best_program[0] = program[:]
                            for _ in range(len(nops_to_add) + 1):
                                program.pop()
                            return
            return
        
        if pos >= max_pos:
            return
        
        # Limit search depth per character
        remaining_chars = len(target) - out_idx
        if pos > (out_idx + 1) * 20:  # Allow up to 20 instructions per output char
            return
        
        avail = available.get(pos, [])
        
        # Try out if A matches
        if 5 in avail and A % 256 == target[out_idx]:
            ch = char_for_op(5, pos)
            program.append(ch)
            dfs(pos + 1, A, out_idx + 1, program)
            if best_program[0] is not None:
                return
            program.pop()
        
        # Try rotr
        if 39 in avail and pos in rotr_result:
            new_A = rotr_result[pos]
            ch = char_for_op(39, pos)
            program.append(ch)
            dfs(pos + 1, new_A, out_idx, program)
            if best_program[0] is not None:
                return
            program.pop()
        
        # Try crz
        if 62 in avail and pos in crz_char:
            new_A = crazy(A, crz_char[pos])
            ch = char_for_op(62, pos)
            program.append(ch)
            dfs(pos + 1, new_A, out_idx, program)
            if best_program[0] is not None:
                return
            program.pop()
        
        # Try nop
        if 68 in avail:
            ch = char_for_op(68, pos)
            program.append(ch)
            dfs(pos + 1, A, out_idx, program)
            if best_program[0] is not None:
                return
            program.pop()
    
    print("Starting DFS search...")
    dfs(0, 0, 0, [])
    
    if best_program[0] is not None:
        return ''.join(chr(c) for c in best_program[0])
    return None


# First let's understand what rotr gives us
print("rotr results at various positions:")
for pos in range(50):
    ch = char_for_op(39, pos)
    if ch is not None:
        r = rotate(ch)
        print(f"  pos {pos}: char {ch} ({chr(ch)}), rotate -> {r}, %256 = {r%256} ({chr(r%256) if 32 <= r%256 < 127 else '?'})")

print()
print("crz with A=0 at various positions:")
for pos in range(50):
    ch = char_for_op(62, pos)
    if ch is not None:
        r = crazy(0, ch)
        print(f"  pos {pos}: char {ch} ({chr(ch)}), crazy(0,{ch}) -> {r}, %256 = {r%256}")

print()
result = search_program("Hello World")
if result:
    print(f"\nGenerated program ({len(result)} chars):")
    print(repr(result))
    
    # Verify
    from malbolge import eval as malbolge_eval
    output = malbolge_eval(result)
    print(f"\nInterpreter output: '{output}'")
    if output.strip() == "Hello World":
        print("SUCCESS!")
    else:
        print(f"MISMATCH: got '{output}', expected 'Hello World'")
else:
    print("\nFailed to find program")
