"""
Debug: check why generated characters are invalid.
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
    ch = (op - pos % 94) % 94 + 33
    if 33 <= ch <= 126:
        return ch
    return None

# Test: verify char_for_op is correct
for pos in range(20):
    for op in OPS_VALID:
        ch = char_for_op(op, pos)
        if ch is not None:
            actual_op = (ch + pos) % 94
            if actual_op != op:
                print(f"BUG: pos={pos}, op={op}, ch={ch}, actual_op={actual_op}")

# Now let's manually check: what does the initialize validator really check?
# From source: if (ord(c)+i) % 94 not in OPS_VALID: halt
# where i is the position counter (incremented for each non-whitespace char)
# and c is the character

# Let me verify with a simple test program
test_ops_sequence = [39, 5, 81]  # rotr, out, end
program = []
for i, op in enumerate(test_ops_sequence):
    ch = char_for_op(op, i)
    program.append(chr(ch))
    print(f"pos {i}: op {op}, char {ch} ({chr(ch)}), verify: (char+pos)%94 = {(ch+i)%94}")

test_code = ''.join(program)
print(f"\nTest program: {repr(test_code)}")

from malbolge import eval as malbolge_eval
try:
    output = malbolge_eval(test_code)
    print(f"Output: {repr(output)}")
except SystemExit as e:
    print(f"SystemExit: {e}")
except Exception as e:
    print(f"Error: {e}")
