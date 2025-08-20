#!/usr/bin/env python3
import os, shutil, math
from PIL import Image, ImageDraw, ImageFont

# ========= SETTINGS =========
# Color options
colors = {
    '1': (255, 0, 0),    # Red
    '2': (0, 255, 0),    # Green
    '3': (0, 0, 255),    # Blue
    '4': (128, 0, 128),  # Purple
    '5': (255, 255, 0),  # Yellow
}
print("Choose background color:")
print("1. Red")
print("2. Green")
print("3. Blue")
print("4. Purple")
print("5. Yellow")
color_choice = input("Enter choice (1-5, default 4): ").strip() or '4'
r, g, b = colors.get(color_choice, (128, 0, 128))  # Default purple
COLOR_BG = f"\033[38;2;{r};{g};{b}m"
RESET = "\033[0m"

TEXT = input("Enter text (default SSOULV): ").strip() or "SSOULV"
FONT_PATH = "GreatVibes-Regular.ttf"
CHAR_BG   = "⣿"
CHAR_EDGE = " "  # Merge edges with empty
CHAR_EMPTY= " "
SCALE = 3          # supersample factor (further reduced to fit terminal)
MARGIN_COLS = 0     # no margins for small terminals
MARGIN_ROWS = 0

# ========= TERMINAL GRID =========
cols, rows = shutil.get_terminal_size()
rows = max(1, rows - 1)  # leave one line for prompt
W, H = cols * SCALE, rows * SCALE

# Measure text at a given font size
def measure(size):
    font = ImageFont.truetype(FONT_PATH, size)
    tmp = Image.new("L", (1, 1), 0)
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), TEXT, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    return font, bbox, w, h

# Find the largest font that fits the terminal grid (with margins)
low, high = 1, 2000
best = None
while low <= high:
    mid = (low + high) // 2
    font, bbox, w, h = measure(mid)
    gw, gh = math.ceil(w / SCALE), math.ceil(h / SCALE)
    if gw <= (cols - 2*MARGIN_COLS) and gh <= (rows - 2*MARGIN_ROWS):
        best = (font, bbox, w, h)
        low = mid + 1
    else:
        high = mid - 1

if best is None:
    raise SystemExit("Font cannot fit the current terminal; reduce SCALE or use a narrower font.")

font, bbox, w, h = best

# Create hi-res canvas and draw text aligned to the terminal grid
img = Image.new("L", (W, H), 0)
draw = ImageDraw.Draw(img)

gw, gh = math.ceil(w / SCALE), math.ceil(h / SCALE)
left_grid = max(0, (cols - gw) // 2)
top_grid  = max(0, (rows - gh) // 2)

# Align the text bbox to the chosen grid cell
x_px = left_grid * SCALE - bbox[0]
y_px = top_grid  * SCALE - bbox[1]
draw.text((x_px, y_px), TEXT, font=font, fill=255)

# Downsample to the exact terminal grid for clean averaging
small = img.resize((cols, rows), Image.BILINEAR)
pix = small.load()

# Thresholds for edge vs empty
T_EDGE  = 40
T_EMPTY = 200

os.system("clear")
for y in range(rows):
    output = []
    for x in range(cols):
        v = pix[x, y]
        if v >= T_EMPTY:
            char = CHAR_EMPTY
            output.append(char)
        elif v >= T_EDGE:
            char = CHAR_EDGE
            output.append(char)
        else:
            char = CHAR_BG
            output.append(COLOR_BG + char + RESET)
    print(''.join(output))
