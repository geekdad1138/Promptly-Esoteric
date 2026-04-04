#!/usr/bin/env python3
"""
Piet interpreter / verifier.
Usage: python verify.py <image_path> [--expected <string>] [--debug]

Interprets a Piet program image and prints the output.
If --expected is given, prints PASS/FAIL based on matching output.
"""

import sys
import argparse
from PIL import Image
from collections import deque

# ── Piet colour table ──────────────────────────────────────────────
# 6 hues × 3 lightness levels  +  white, black
COLOUR_TABLE = {
    # Light
    (0xFF, 0xC0, 0xC0): (0, 0),  # light red
    (0xFF, 0xFF, 0xC0): (1, 0),  # light yellow
    (0xC0, 0xFF, 0xC0): (2, 0),  # light green
    (0xC0, 0xFF, 0xFF): (3, 0),  # light cyan
    (0xC0, 0xC0, 0xFF): (4, 0),  # light blue
    (0xFF, 0xC0, 0xFF): (5, 0),  # light magenta
    # Normal
    (0xFF, 0x00, 0x00): (0, 1),  # red
    (0xFF, 0xFF, 0x00): (1, 1),  # yellow
    (0x00, 0xFF, 0x00): (2, 1),  # green
    (0x00, 0xFF, 0xFF): (3, 1),  # cyan
    (0x00, 0x00, 0xFF): (4, 1),  # blue
    (0xFF, 0x00, 0xFF): (5, 1),  # magenta
    # Dark
    (0xC0, 0x00, 0x00): (0, 2),  # dark red
    (0xC0, 0xC0, 0x00): (1, 2),  # dark yellow
    (0x00, 0xC0, 0x00): (2, 2),  # dark green
    (0x00, 0xC0, 0xC0): (3, 2),  # dark cyan
    (0x00, 0x00, 0xC0): (4, 2),  # dark blue
    (0xC0, 0x00, 0xC0): (5, 2),  # dark magenta
}

WHITE = (0xFF, 0xFF, 0xFF)
BLACK = (0x00, 0x00, 0x00)

# Direction Pointer: right=0, down=1, left=2, up=3
DP_DELTAS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # (dx, dy)

# ── Helper: classify a pixel ──────────────────────────────────────
def classify(rgb):
    """Return 'white', 'black', or (hue, lightness) tuple."""
    r, g, b = rgb[0], rgb[1], rgb[2]
    key = (r, g, b)
    if key == WHITE:
        return "white"
    if key == BLACK:
        return "black"
    if key in COLOUR_TABLE:
        return COLOUR_TABLE[key]
    # Treat unknown colours as white (per spec)
    return "white"


# ── Flood-fill to find a colour block ─────────────────────────────
def flood_fill(grid, width, height, start_x, start_y, target_class):
    """Return the set of (x,y) codels in the same colour block."""
    block = set()
    queue = deque()
    queue.append((start_x, start_y))
    block.add((start_x, start_y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in block:
                if classify(grid[ny][nx]) == target_class:
                    block.add((nx, ny))
                    queue.append((nx, ny))
    return block


# ── Main interpreter ──────────────────────────────────────────────
def interpret(image_path, debug=False):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = img.load()

    # Build 2-D grid
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(pixels[x, y])
        grid.append(row)

    # Cache: (x,y) -> block set
    block_cache = {}

    def get_block(x, y):
        if (x, y) in block_cache:
            return block_cache[(x, y)]
        cls = classify(grid[y][x])
        if cls in ("white", "black"):
            b = frozenset([(x, y)])
        else:
            b = frozenset(flood_fill(grid, width, height, x, y, cls))
        for cx, cy in b:
            block_cache[(cx, cy)] = b
        return b

    # State
    dp = 0       # direction pointer (0=right, 1=down, 2=left, 3=up)
    cc = 0       # codel chooser (0=left, 1=right)
    cx, cy = 0, 0  # current codel position
    stack = []
    output = []
    max_steps = 100000
    step = 0

    def current_class():
        return classify(grid[cy][cx])

    def find_exit_codel(block, dp_dir, cc_dir):
        """
        Find the exit codel from a block given DP direction and CC direction.
        1. Find the edge furthest in DP direction.
        2. Among those, pick the codel furthest in CC's direction relative to DP.
        """
        dx_dp, dy_dp = DP_DELTAS[dp_dir]

        # The "furthest in DP direction" means max projection onto DP vector
        max_proj = None
        for bx, by in block:
            proj = bx * dx_dp + by * dy_dp
            if max_proj is None or proj > max_proj:
                max_proj = proj

        # Gather all codels on that edge
        edge_codels = [(bx, by) for bx, by in block
                       if bx * dx_dp + by * dy_dp == max_proj]

        # CC direction relative to DP:
        # If DP=right(0), CC-left means up(-y), CC-right means down(+y)
        # If DP=down(1),  CC-left means right(+x), CC-right means left(-x)
        # If DP=left(2),  CC-left means down(+y), CC-right means up(-y)
        # If DP=up(3),    CC-left means left(-x), CC-right means right(+x)
        # CC perpendicular: turn left from DP = (dp-1)%4, turn right = (dp+1)%4
        if cc_dir == 0:  # CC pointing left -> turn left from DP direction
            perp = (dp_dir + 3) % 4   # counterclockwise
        else:            # CC pointing right -> turn right from DP direction
            perp = (dp_dir + 1) % 4   # clockwise

        dx_cc, dy_cc = DP_DELTAS[perp]

        # Pick the codel with maximum projection onto the CC perpendicular
        best = None
        best_proj = None
        for bx, by in edge_codels:
            p = bx * dx_cc + by * dy_cc
            if best_proj is None or p > best_proj:
                best_proj = p
                best = (bx, by)
        return best

    while step < max_steps:
        step += 1
        cls = current_class()

        if cls in ("white", "black"):
            # Shouldn't start on black; if white, slide
            if cls == "white":
                # Slide in DP direction
                moved = False
                attempts = 0
                while attempts < 8:
                    dx, dy = DP_DELTAS[dp]
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        ncls = classify(grid[ny][nx])
                        if ncls == "white":
                            cx, cy = nx, ny
                            continue  # keep sliding
                        elif ncls == "black":
                            # hit restriction while in white
                            cc = 1 - cc
                            dp = (dp + 1) % 4
                            attempts += 1
                            continue
                        else:
                            # entered a colour block, no command executed
                            cx, cy = nx, ny
                            moved = True
                            break
                    else:
                        # hit edge while in white
                        cc = 1 - cc
                        dp = (dp + 1) % 4
                        attempts += 1
                        continue
                if not moved and attempts >= 8:
                    break  # trapped
                continue

        # We're on a coloured block
        block = get_block(cx, cy)
        block_size = len(block)
        block_cls = cls  # (hue, lightness)

        # Try to exit this block
        attempts = 0
        moved = False
        while attempts < 8:
            exit_codel = find_exit_codel(block, dp, cc)
            ex, ey = exit_codel
            dx, dy = DP_DELTAS[dp]
            nx, ny = ex + dx, ey + dy

            if 0 <= nx < width and 0 <= ny < height:
                ncls = classify(grid[ny][nx])
                if ncls == "black":
                    # blocked
                    if attempts % 2 == 0:
                        cc = 1 - cc
                    else:
                        dp = (dp + 1) % 4
                    attempts += 1
                    continue
                elif ncls == "white":
                    # Move into white, then slide
                    cx, cy = nx, ny
                    # Slide through white
                    slide_attempts = 0
                    while slide_attempts < 8:
                        sdx, sdy = DP_DELTAS[dp]
                        snx, sny = cx + sdx, cy + sdy
                        if 0 <= snx < width and 0 <= sny < height:
                            scls = classify(grid[sny][snx])
                            if scls == "white":
                                cx, cy = snx, sny
                                continue
                            elif scls == "black":
                                cc = 1 - cc
                                dp = (dp + 1) % 4
                                slide_attempts += 1
                                continue
                            else:
                                # Reached a coloured block via white - NO command
                                cx, cy = snx, sny
                                moved = True
                                break
                        else:
                            # hit edge
                            cc = 1 - cc
                            dp = (dp + 1) % 4
                            slide_attempts += 1
                            continue
                    if moved:
                        break
                    if slide_attempts >= 8:
                        break  # trapped in white
                    break
                else:
                    # Moving into another colour block - execute command
                    new_hue, new_light = ncls
                    old_hue, old_light = block_cls

                    d_hue = (new_hue - old_hue) % 6
                    d_light = (new_light - old_light) % 3

                    if debug:
                        cmd_name = get_command_name(d_hue, d_light)
                        print(f"Step {step}: block_size={block_size}, "
                              f"({old_hue},{old_light})->({new_hue},{new_light}), "
                              f"dH={d_hue} dL={d_light} => {cmd_name}")

                    execute_command(d_hue, d_light, block_size, stack, output, dp, cc)
                    # Update dp/cc if pointer/switch was executed
                    dp, cc = execute_dp_cc(d_hue, d_light, stack, dp, cc)

                    cx, cy = nx, ny
                    moved = True
                    break
            else:
                # Off edge
                if attempts % 2 == 0:
                    cc = 1 - cc
                else:
                    dp = (dp + 1) % 4
                attempts += 1
                continue

        if not moved:
            if debug:
                print(f"Program terminated at step {step} (trapped)")
            break

    return "".join(output)


def get_command_name(d_hue, d_light):
    commands = [
        ["nop",      "push",     "pop",      "add",      "subtract", "multiply"],
        ["divide",   "mod",      "not",      "greater",  "pointer",  "switch"],
        ["duplicate","roll",     "in(num)",  "in(char)", "out(num)", "out(char)"],
    ]
    return commands[d_light][d_hue]


def execute_command(d_hue, d_light, block_size, stack, output, dp, cc):
    """Execute the command, modifying stack and output in place.
    Does NOT handle pointer/switch (those modify dp/cc and are handled separately).
    """
    if d_light == 0:
        if d_hue == 0:
            pass  # nop
        elif d_hue == 1:  # push
            stack.append(block_size)
        elif d_hue == 2:  # pop
            if stack:
                stack.pop()
        elif d_hue == 3:  # add
            if len(stack) >= 2:
                a = stack.pop()
                b = stack.pop()
                stack.append(b + a)
        elif d_hue == 4:  # subtract
            if len(stack) >= 2:
                a = stack.pop()
                b = stack.pop()
                stack.append(b - a)
        elif d_hue == 5:  # multiply
            if len(stack) >= 2:
                a = stack.pop()
                b = stack.pop()
                stack.append(b * a)
    elif d_light == 1:
        if d_hue == 0:  # divide
            if len(stack) >= 2:
                a = stack.pop()
                b = stack.pop()
                if a != 0:
                    stack.append(int(b / a))
                else:
                    stack.append(b)
                    stack.append(a)
        elif d_hue == 1:  # mod
            if len(stack) >= 2:
                a = stack.pop()
                b = stack.pop()
                if a != 0:
                    stack.append(b % a)
                else:
                    stack.append(b)
                    stack.append(a)
        elif d_hue == 2:  # not
            if stack:
                val = stack.pop()
                stack.append(0 if val != 0 else 1)
        elif d_hue == 3:  # greater
            if len(stack) >= 2:
                a = stack.pop()
                b = stack.pop()
                stack.append(1 if b > a else 0)
        # pointer and switch are handled separately
    elif d_light == 2:
        if d_hue == 0:  # duplicate
            if stack:
                stack.append(stack[-1])
        elif d_hue == 1:  # roll
            if len(stack) >= 2:
                rolls = stack.pop()
                depth = stack.pop()
                if depth > 0 and depth <= len(stack):
                    segment = stack[-depth:]
                    rolls = rolls % depth
                    if rolls != 0:
                        rolled = segment[-rolls:] + segment[:-rolls]
                        stack[-depth:] = rolled
        elif d_hue == 2:  # in(num)
            pass  # no stdin in verify mode
        elif d_hue == 3:  # in(char)
            pass  # no stdin in verify mode
        elif d_hue == 4:  # out(num)
            if stack:
                val = stack.pop()
                output.append(str(val))
        elif d_hue == 5:  # out(char)
            if stack:
                val = stack.pop()
                output.append(chr(val))


def execute_dp_cc(d_hue, d_light, stack, dp, cc):
    """Handle pointer and switch commands that modify dp/cc."""
    if d_light == 1:
        if d_hue == 4:  # pointer
            if stack:
                val = stack.pop()
                dp = (dp + val) % 4
        elif d_hue == 5:  # switch
            if stack:
                val = stack.pop()
                if abs(val) % 2 == 1:
                    cc = 1 - cc
    return dp, cc


# ── Main ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Piet interpreter / verifier")
    parser.add_argument("image", help="Path to the Piet program image")
    parser.add_argument("--expected", default=None,
                        help="Expected output string")
    parser.add_argument("--debug", action="store_true",
                        help="Print debug trace")
    args = parser.parse_args()

    result = interpret(args.image, debug=args.debug)
    print(f"Output: {result}")

    if args.expected is not None:
        if result == args.expected:
            print("PASS")
        else:
            print(f"FAIL (expected '{args.expected}', got '{result}')")
            sys.exit(1)


if __name__ == "__main__":
    main()
