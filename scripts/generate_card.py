import os
import math
import requests
import numpy as np
from PIL import Image

# ==============================================================================
# USER CONFIGURATION & PROFILE DATA
# ==============================================================================

# GitHub username
LOGIN = os.getenv("GITHUB_LOGIN", "melvine-p")

# Profile fields rendered on the card
PROFILE_FIELDS = [
    ("Name", "Neil Melvine M. Togado"),
    ("Role", "Aspiring Software Developer"),
    ("Location", "Boac, Marinduque, PH"),
    ("Education", "BS Computer Engineering (4th Yr)"),
    ("Stack.Frontend", "HTML, CSS, JS, TS, React, Next.js"),
    ("Stack.Backend", "Node.js, MySQL, PostgreSQL"),
    ("Stack.Mobile", "React Native"),
    ("Security", "JWT, bcrypt, OAuth, Auth0"),
    ("Tools", "GitHub, VSCode, Arduino IDE"),
    ("Contact.Email", "melvinetogado1@gmail.com"),
    ("Contact.Phone", "09155871671"),
    ("Contact.GitHub", f"github.com/{LOGIN}"),
    ("Contact.LinkedIn", "linkedin.com/in/neil-melvine-togado-51a111438"),
]

# Animated prompt commands (types out sequentially in the terminal card)
PROMPT_COMMANDS = [
    "aspiring software developer",
    "bs computer engineering student",
    "web and mobile development",
    "actively seeking ojt / internship",
]

# Styling & Palette
BG_COLOR = "#0b1120"       # Window background
TITLEBAR_COLOR = "#141c30" # Titlebar strip background
ACCENT = "#5dc9f2"         # ASCII art color
HEADER_COLOR = "#e8384f"    # Prompt / login header color
LABEL_COLOR = "#ffffff"     # Field label color
VALUE_COLOR = "#5dc9f2"     # Field value color

PALETTE = [
    "#0b1120", "#e8384f", "#3ddc84", "#ffd166",
    "#4d8cff", "#b16cff", "#39e0d0", "#e8e8e8"
]

# Grid / Animation specs
ART_COLS = 34
PROMPT_TYPE_SPEED = 0.08
PROMPT_DELETE_SPEED = 0.045
PROMPT_HOLD_TIME = 1.1
PROMPT_GAP_TIME = 0.4

# ASCII character ramp (from dark to light)
ASCII_RAMP = " .:-=+*#%@"


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def xml_escape_text(text):
    """Escapes XML characters for inner text nodes."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def css_escape_string(text):
    """Escapes quotes and backslashes for CSS string literals."""
    return str(text).replace("\\", "\\\\").replace('"', '\\"')

def get_avatar_ascii(avatar_path, cols=34):
    """Loads image, converts to square grayscale, downsamples, and returns ASCII lines."""
    if not os.path.exists(avatar_path):
        return None
    try:
        img = Image.open(avatar_path).convert("L")
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))
        
        # Terminal characters are roughly 1:2 aspect ratio
        rows = int(cols * 0.55)
        img = img.resize((cols, rows), Image.Resampling.LANCZOS)
        
        arr = np.array(img)
        lines = []
        for r in range(rows):
            line = ""
            for c in range(cols):
                val = arr[r, c]
                idx = int((val / 255.0) * (len(ASCII_RAMP) - 1))
                line += ASCII_RAMP[idx]
            lines.append(line)
        return lines
    except Exception:
        return None

def get_procedural_dragon(cols=34):
    """Fallback ASCII dragon motif if no avatar image is supplied."""
    dragon_art = [
        "         ,     .-'\"'-.",
        "        /|   .'  ,-.  \\",
        "       / |  /   /   |  |",
        "      |  | |   |    |  |",
        "      |  | |   |    |  |",
        "     /   | |   |    |  |",
        "    |    | |    '--'   |",
        "    |    '-'          /",
        "     \\               /",
        "      '.           .'",
        "        '--.____.-'",
        "          /      \\",
        "         |  o  o  |",
        "         |   \\/   |",
        "          \\  --  /",
        "           '.__.'",
        "          /  |   \\",
        "         /   |    \\",
    ]
    return [line.ljust(cols)[:cols] for line in dragon_art]

def fetch_github_stats(username, token=None):
    """Fetches user repository and follower stats from GitHub API."""
    stats = {"repos": "N/A", "followers": "N/A"}
    if not username:
        return stats
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        res = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            stats["repos"] = str(data.get("public_repos", "N/A"))
            stats["followers"] = str(data.get("followers", "N/A"))
    except Exception:
        pass
    return stats


def generate_svg(avatar_lines, stats, login):
    """Renders terminal card, ASCII art, details, and CSS typing animations to SVG."""
    gh_login = login.lower()
    
    # CSS typing keyframe generation
    total_time = 0.0
    command_timings = []

    for cmd in PROMPT_COMMANDS:
        t_type = len(cmd) * PROMPT_TYPE_SPEED
        t_hold = PROMPT_HOLD_TIME
        t_delete = len(cmd) * PROMPT_DELETE_SPEED
        t_gap = PROMPT_GAP_TIME
        duration = t_type + t_hold + t_delete + t_gap
        command_timings.append((cmd, duration, t_type, t_hold, t_delete, t_gap))
        total_time += duration

    # SVG layout measurements
    char_w = 7.8
    line_h = 15
    pad_x = 20
    pad_y = 20
    header_h = 30

    art_width_px = ART_COLS * char_w
    art_height_lines = len(avatar_lines)
    
    # Build layout rows
    right_rows = [f"{gh_login}@github", "-" * (len(gh_login) + 7)]
    for label, val in PROFILE_FIELDS:
        right_rows.append((label, val))
    
    right_rows.append(("GitHub.Repos", stats["repos"]))
    right_rows.append(("GitHub.Followers", stats["followers"]))

    total_lines = max(art_height_lines, len(right_rows)) + 3
    svg_w = 750
    svg_h = header_h + pad_y * 2 + (total_lines * line_h) + 40

    # Build ASCII XML text
    ascii_svg_text = ""
    for idx, line in enumerate(avatar_lines):
        escaped_line = xml_escape_text(line).replace(" ", "&#160;")
        y_pos = header_h + pad_y + (idx * line_h) + 12
        ascii_svg_text += f'<tspan x="{pad_x}" y="{y_pos}">{escaped_line}</tspan>\n'

    # Build info text XML
    info_x = pad_x + art_width_px + 30
    info_svg_text = ""
    for idx, row in enumerate(right_rows):
        y_pos = header_h + pad_y + (idx * line_h) + 12
        if isinstance(row, tuple):
            label, val = row
            escaped_label = xml_escape_text(label)
            escaped_val = xml_escape_text(val)
            info_svg_text += f'<tspan x="{info_x}" y="{y_pos}"><tspan fill="{LABEL_COLOR}" font-weight="bold">{escaped_label}:</tspan> <tspan fill="{VALUE_COLOR}">{escaped_val}</tspan></tspan>\n'
        else:
            escaped_row = xml_escape_text(row)
            info_svg_text += f'<tspan x="{info_x}" y="{y_pos}" fill="{HEADER_COLOR}" font-weight="bold">{escaped_row}</tspan>\n'

    # Color palette swatch strip
    swatch_y = header_h + pad_y + ((total_lines - 2) * line_h) + 10
    swatch_svg = ""
    for idx, col in enumerate(PALETTE):
        sx = info_x + (idx * 22)
        swatch_svg += f'<rect x="{sx}" y="{swatch_y}" width="18" height="10" fill="{col}" rx="2" />\n'

    # Prompt line offset
    prompt_y = swatch_y + 25

    # CSS Typing keyframe generator
    keyframes_css = "@keyframes typeSequence {\n"
    curr_time = 0.0
    for cmd, duration, t_type, t_hold, t_delete, t_gap in command_timings:
        p0 = (curr_time / total_time) * 100
        p1 = ((curr_time + t_type) / total_time) * 100
        p2 = ((curr_time + t_type + t_hold) / total_time) * 100
        p3 = ((curr_time + t_type + t_hold + t_delete) / total_time) * 100
        p4 = ((curr_time + duration) / total_time) * 100

        keyframes_css += f'  {p0:.2f}% {{ content: "$ "; }}\n'
        for i in range(1, len(cmd) + 1):
            sub_p = p0 + (i / len(cmd)) * (p1 - p0)
            sub_str = css_escape_string(cmd[:i])
            keyframes_css += f'  {sub_p:.2f}% {{ content: "$ {sub_str}"; }}\n'
        
        escaped_cmd = css_escape_string(cmd)
        keyframes_css += f'  {p2:.2f}% {{ content: "$ {escaped_cmd}"; }}\n'
        for i in range(len(cmd) - 1, -1, -1):
            sub_p = p2 + ((len(cmd) - i) / len(cmd)) * (p3 - p2)
            sub_str = css_escape_string(cmd[:i])
            keyframes_css += f'  {sub_p:.2f}% {{ content: "$ {sub_str}"; }}\n'

        keyframes_css += f'  {p4:.2f}% {{ content: "$ "; }}\n'
        curr_time += duration

    keyframes_css += "}\n"

    # SVG markup template
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
  <style>
    .terminal-bg {{ fill: {BG_COLOR}; }}
    .titlebar {{ fill: {TITLEBAR_COLOR}; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .title-text {{ fill: #8b949e; font-family: monospace; font-size: 12px; }}
    .code-text {{ font-family: 'Courier New', Courier, monospace; font-size: 12px; white-space: pre; }}
    .prompt::after {{
      content: "$ ";
      animation: typeSequence {total_time:.2f}s infinite;
      color: {HEADER_COLOR};
      font-weight: bold;
    }}
    .cursor {{
      animation: blink 0.8s infinite;
      fill: {HEADER_COLOR};
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0; }}
    }}
    {keyframes_css}
  </style>

  <!-- Window Container -->
  <rect width="{svg_w}" height="{svg_h}" rx="8" class="terminal-bg" />
  
  <!-- Titlebar -->
  <path d="M 0 8 C 0 3, 3 0, 8 0 L {svg_w - 8} 0 C {svg_w - 3} 0, {svg_w} 3, {svg_w} 8 L {svg_w} {header_h} L 0 {header_h} Z" class="titlebar" />
  <circle cx="18" cy="15" r="5" class="dot-red" />
  <circle cx="34" cy="15" r="5" class="dot-yellow" />
  <circle cx="50" cy="15" r="5" class="dot-green" />
  <text x="{svg_w / 2}" y="19" text-anchor="middle" class="title-text">{gh_login}@terminal:~</text>

  <!-- ASCII Art Column -->
  <text class="code-text" fill="{ACCENT}">
{ascii_svg_text}  </text>

  <!-- Info Columns -->
  <text class="code-text">
{info_svg_text}  </text>

  <!-- Color Swatches -->
{swatch_svg}

  <!-- Animated Prompt -->
  <text x="{info_x}" y="{prompt_y}" class="code-text prompt" />
  <rect x="{info_x + 280}" y="{prompt_y - 10}" width="7" height="12" class="cursor" />
</svg>
"""
    return svg_content


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    avatar_path = os.getenv("AVATAR_PATH", "assets/avatar.jpg")
    out_path = os.getenv("OUT_PATH", "assets/profile.svg")
    github_token = os.getenv("GITHUB_TOKEN", None)

    # Process Avatar
    avatar_lines = get_avatar_ascii(avatar_path, cols=ART_COLS)
    if not avatar_lines:
        avatar_lines = get_procedural_dragon(cols=ART_COLS)

    # Fetch live stats
    stats = fetch_github_stats(LOGIN, token=github_token)

    # Generate and write output SVG
    svg_data = generate_svg(avatar_lines, stats, LOGIN)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_data)

    print(f"Card successfully generated at: {out_path}")

if __name__ == "__main__":
    main()
