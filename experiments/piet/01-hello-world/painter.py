"""
Piet "Hello" Painter
Generates a hello.png that, when interpreted by a Piet interpreter,
outputs the string "Hello".

Strategy:
  Use small color blocks with arithmetic operations (push, multiply, add)
  to build ASCII values, then out_char to print them.

  ASCII values: H=72, e=101, l=108, l=108, o=111

  Decompositions (keeping block sizes small):
    H = 72  = 8 * 9           → push 8, push 9, multiply, outC
    e = 101 = 10 * 10 + 1     → push 10, push 10, multiply, push 1, add, outC
    l = 108 = 9 * 12           → push 9, push 12, multiply, outC
    l = 108 = 9 * 12           → push 9, push 12, multiply, outC
    o = 111 = 12 * 9 + 3      → push 12, push 9, multiply, push 3, add, outC

Color System (from PietInterpreter):
  18 colors: 6 hues × 3 lightnesses
  Index = hue * 3 + lightness
  
  hueChange   = (endHue - startHue) % 6
  lightChange = (endIndex - startIndex) % 3

  Operations used:
    push:     hue_change=0, light_change=1
    add:      hue_change=1, light_change=0
    multiply: hue_change=1, light_change=2
    out_char: hue_change=5, light_change=2
"""

from PIL import Image
import os

# The 18 Piet colors in order (index 0-17)
COLORS = [
    (255, 192, 192),  # 0:  Light Red
    (255,   0,   0),  # 1:  Red
    (192,   0,   0),  # 2:  Dark Red
    (255, 255, 192),  # 3:  Light Yellow
    (255, 255,   0),  # 4:  Yellow
    (192, 192,   0),  # 5:  Dark Yellow
    (192, 255, 192),  # 6:  Light Green
    (  0, 255,   0),  # 7:  Green
    (  0, 192,   0),  # 8:  Dark Green
    (192, 255, 255),  # 9:  Light Cyan
    (  0, 255, 255),  # 10: Cyan
    (  0, 192, 192),  # 11: Dark Cyan
    (192, 192, 255),  # 12: Light Blue
    (  0,   0, 255),  # 13: Blue
    (  0,   0, 192),  # 14: Dark Blue
    (255, 192, 255),  # 15: Light Magenta
    (255,   0, 255),  # 16: Magenta
    (192,   0, 192),  # 17: Dark Magenta
]

BLACK = (0, 0, 0)

# Operation definitions: (hue_change, light_change)
OP_PUSH     = (0, 1)
OP_ADD      = (1, 0)
OP_MULTIPLY = (1, 2)
OP_OUTCHAR  = (5, 2)


def find_next_color(start_index, hue_change, light_change):
    """
    Find the color index that, when transitioned TO from start_index,
    produces the given hue_change and light_change.
    """
    start_hue = start_index // 3
    start_light = start_index % 3
    end_hue = (start_hue + hue_change) % 6
    end_light = (start_light + light_change) % 3
    return end_hue * 3 + end_light


def add_operation(blocks, current_color, op, codel_size=1):
    """
    Add a single operation to the block list.
    
    For PUSH: the codel_size of the SOURCE block determines the pushed value.
    For other ops: codel_size of source doesn't matter (we use 1).
    
    Args:
        blocks: list of (color_index, width) to append to
        current_color: current color index
        op: tuple of (hue_change, light_change)
        codel_size: width of the source block (only matters for push)
    
    Returns:
        next color index (the destination color)
    """
    # The source block is already placed (or will be placed by caller for push)
    next_color = find_next_color(current_color, op[0], op[1])
    return next_color


def build_hello_blocks():
    """
    Build the block sequence for "Hello".
    
    Each operation is a transition between adjacent blocks.
    The PUSH operation pushes the size of the SOURCE codel.
    """
    blocks = []  # (color_index, width)
    current = 0  # Start at color index 0 (Light Red)
    
    # === 'H' = 72 = 8 * 9 ===
    # push 8
    blocks.append((current, 8))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # push 9
    blocks.append((current, 9))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # multiply (codel size doesn't matter for non-push ops, use 1)
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_MULTIPLY)
    current = next_c
    
    # out_char
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_OUTCHAR)
    current = next_c
    
    # === 'e' = 101 = 10 * 10 + 1 ===
    # push 10
    blocks.append((current, 10))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # push 10
    blocks.append((current, 10))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # multiply
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_MULTIPLY)
    current = next_c
    
    # push 1
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # add
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_ADD)
    current = next_c
    
    # out_char
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_OUTCHAR)
    current = next_c
    
    # === 'l' = 108 = 9 * 12 ===
    # push 9
    blocks.append((current, 9))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # push 12
    blocks.append((current, 12))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # multiply
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_MULTIPLY)
    current = next_c
    
    # out_char
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_OUTCHAR)
    current = next_c
    
    # === 'l' = 108 = 9 * 12 ===
    # push 9
    blocks.append((current, 9))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # push 12
    blocks.append((current, 12))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # multiply
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_MULTIPLY)
    current = next_c
    
    # out_char
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_OUTCHAR)
    current = next_c
    
    # === 'o' = 111 = 12 * 9 + 3 ===
    # push 12
    blocks.append((current, 12))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # push 9
    blocks.append((current, 9))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # multiply
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_MULTIPLY)
    current = next_c
    
    # push 3
    blocks.append((current, 3))
    next_c = find_next_color(current, *OP_PUSH)
    current = next_c
    
    # add
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_ADD)
    current = next_c
    
    # out_char — need a destination block for the outC transition to fire
    blocks.append((current, 1))
    next_c = find_next_color(current, *OP_OUTCHAR)
    current = next_c
    
    # Final block: the outC destination. After this, pointer hits black/edge → terminate
    blocks.append((current, 1))
    
    return blocks


def verify_blocks(blocks):
    """Verify all transitions produce the expected operations."""
    from PietInterpreter.tokens import getTokenType
    
    print("Transition verification:")
    stack = []
    
    for i in range(len(blocks) - 1):
        src_idx, src_width = blocks[i]
        dst_idx, _ = blocks[i + 1]
        
        hue_change = (dst_idx // 3 - src_idx // 3) % 6
        light_change = (dst_idx - src_idx) % 3
        token_type = getTokenType(hue_change, light_change)
        
        # Simulate
        detail = ""
        if token_type == "push":
            stack.append(src_width)
            detail = f" → stack: {stack}"
        elif token_type == "multiply":
            if len(stack) >= 2:
                b = stack.pop()
                a = stack.pop()
                stack.append(a * b)
            detail = f" → stack: {stack}"
        elif token_type == "add":
            if len(stack) >= 2:
                b = stack.pop()
                a = stack.pop()
                stack.append(a + b)
            detail = f" → stack: {stack}"
        elif token_type == "outC":
            if stack:
                val = stack.pop()
                detail = f" → outputs '{chr(val)}' (ASCII {val}), stack: {stack}"
        
        print(f"  [{i:2d}] color {src_idx:2d} (w={src_width:2d}) → color {dst_idx:2d}: "
              f"hue={hue_change} light={light_change} = {token_type:8s}{detail}")
    
    # Last block info
    last_idx, last_width = blocks[-1]
    print(f"  [{len(blocks)-1:2d}] color {last_idx:2d} (w={last_width:2d}) → BLACK (terminate)")


def create_image(blocks, output_path):
    """Create a 1-pixel-tall PNG from the block list."""
    total_width = sum(width for _, width in blocks) + 1  # +1 for black terminator
    
    img = Image.new("RGB", (total_width, 1))
    
    x = 0
    for color_index, width in blocks:
        color = COLORS[color_index]
        for i in range(width):
            img.putpixel((x + i, 0), color)
        x += width
    
    # Black termination pixel
    img.putpixel((x, 0), BLACK)
    
    img.save(output_path)
    print(f"\nGenerated {output_path} ({total_width}x1 pixels)")


def main():
    blocks = build_hello_blocks()
    verify_blocks(blocks)
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hello.png")
    create_image(blocks, output_path)


if __name__ == "__main__":
    main()
