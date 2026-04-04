#!/usr/bin/env python3
"""
Piet "Hello" painter.

Generates a hello.png whose colour transitions push ASCII values for
"H", "e", "l", "l", "o" onto the stack and print them as characters.

Strategy
--------
Single row of codels, interpreter moves left → right (DP=right).

For each character c in "Hello":
  1. A colour block of ord(c) codels  → exiting triggers PUSH
  2. A 1-codel block                  → entering triggers PUSH, exiting triggers OUT(char)

The OUT(char) command fires on the *transition into* the next block.
So for the final character we still need a "landing" codel whose colour
creates the correct ΔHue/ΔLightness for OUT(char).  After that, a black
codel terminates the program.

Piet command encoding:
  PUSH      = ΔHue 1,  ΔLightness 0
  OUT(char) = ΔHue 5,  ΔLightness 2
"""

from PIL import Image

# ── Piet colour definitions ───────────────────────────────────────
# Indexed by (hue, lightness) where hue ∈ [0..5], lightness ∈ [0..2]
#   hue:  0=Red, 1=Yellow, 2=Green, 3=Cyan, 4=Blue, 5=Magenta
#   lightness: 0=Light, 1=Normal, 2=Dark
PIET_COLOURS = {
    (0, 0): (0xFF, 0xC0, 0xC0),  # light red
    (1, 0): (0xFF, 0xFF, 0xC0),  # light yellow
    (2, 0): (0xC0, 0xFF, 0xC0),  # light green
    (3, 0): (0xC0, 0xFF, 0xFF),  # light cyan
    (4, 0): (0xC0, 0xC0, 0xFF),  # light blue
    (5, 0): (0xFF, 0xC0, 0xFF),  # light magenta
    (0, 1): (0xFF, 0x00, 0x00),  # red
    (1, 1): (0xFF, 0xFF, 0x00),  # yellow
    (2, 1): (0x00, 0xFF, 0x00),  # green
    (3, 1): (0x00, 0xFF, 0xFF),  # cyan
    (4, 1): (0x00, 0x00, 0xFF),  # blue
    (5, 1): (0xFF, 0x00, 0xFF),  # magenta
    (0, 2): (0xC0, 0x00, 0x00),  # dark red
    (1, 2): (0xC0, 0xC0, 0x00),  # dark yellow
    (2, 2): (0x00, 0xC0, 0x00),  # dark green
    (3, 2): (0x00, 0xC0, 0xC0),  # dark cyan
    (4, 2): (0x00, 0x00, 0xC0),  # dark blue
    (5, 2): (0xC0, 0x00, 0xC0),  # dark magenta
}

BLACK = (0x00, 0x00, 0x00)


def get_colour(hue, lightness):
    return PIET_COLOURS[(hue % 6, lightness % 3)]


def main():
    message = "Hello"

    # Build the colour sequence as a list of (rgb, count) segments.
    # Starting colour: hue=0 (Red), lightness=0 (Light)  →  Light Red
    hue = 0
    lightness = 0
    segments = []

    for ch in message:
        ascii_val = ord(ch)

        # ── Block of `ascii_val` codels ──
        # Exiting this block triggers PUSH (block size = ascii_val).
        colour = get_colour(hue, lightness)
        segments.append((colour, ascii_val))

        # Transition: PUSH  →  ΔHue=1, ΔLightness=0
        hue = (hue + 1) % 6
        # lightness unchanged

        # ── 1-codel intermediary ──
        # Entering this block executes the PUSH above.
        # Exiting this block into the NEXT block executes OUT(char).
        colour = get_colour(hue, lightness)
        segments.append((colour, 1))

        # Transition: OUT(char)  →  ΔHue=5, ΔLightness=2
        hue = (hue + 5) % 6
        lightness = (lightness + 2) % 3

    # ── Landing codel ──
    # The last out(char) fires when the interpreter enters this block.
    # After this, the black codel terminates the program.
    colour = get_colour(hue, lightness)
    segments.append((colour, 1))

    # Total width = sum of all segment counts + 1 (for terminating black)
    total_width = sum(count for _, count in segments) + 1

    # Create the image — single row
    img = Image.new("RGB", (total_width, 1))
    pixels = img.load()

    x = 0
    for colour, count in segments:
        for i in range(count):
            pixels[x, 0] = colour
            x += 1

    # Terminating black codel
    pixels[x, 0] = BLACK

    output_path = "experiments/piet/01-hello-world/hello.png"
    img.save(output_path)
    print(f"Generated {output_path}  ({total_width}×1 pixels)")
    print(f"Colour segments:")
    for colour, count in segments:
        hname = next(
            (f"({h},{l})" for (h, l), c in PIET_COLOURS.items() if c == colour),
            "???",
        )
        print(f"  {hname}  #{colour[0]:02X}{colour[1]:02X}{colour[2]:02X}"
              f"  × {count}")
    print(f"  BLACK  #000000  × 1  (terminator)")


if __name__ == "__main__":
    main()
