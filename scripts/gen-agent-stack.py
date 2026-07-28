#!/usr/bin/env python3
"""Generate a static, self-contained "The Fleet" agent-stack card SVG.

Renders the Fleet (Frameworks / Agents / Retired) as one lapis-themed card in
the EXACT same design language as gen-model-fleet.py — bordered surface with a
starfield + radial glow, a brushed-metal gold top edge, gradient gem tiles and
raised badges, a sparkle title with a tracked subtitle, right-aligned per-row
status pills (LIVE / RETIRED) tied to short rows by a dashed guide line, and a
soft pulse on the live dots. Zero external runtime dependency.

The matrix skeleton mirrors model-fleet (left category column + right content
column + row structure), but each category's badge flow wraps inside its row so
the dense Agents roster stays narrow and the card width rhymes with the model
card instead of ballooning. The left tile + name are vertically centred across
a category's wrapped lines; the status pill anchors to the first line.

Static by design: edit ROWS below and re-run to refresh.

    python scripts/gen-agent-stack.py

Brand logos (the small glyph inside each badge) are from simple-icons
(github.com/simple-icons/simple-icons), CC0-1.0, each on a 24x24 viewBox.
Category glyphs (the gem-tile mark) are hand-drawn.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _backup import add_backup_args, maybe_snapshot  # noqa: E402

# --- lapis theme (shared with gen-stats-card.py / gen-model-fleet.py) -------
BG = "#0A1633"          # card surface
BORDER = "#1E2A54"      # card border / live-pill stroke
TILE_TOP = "#34599F"    # active gem-tile gradient top
TILE_BOT = "#21407A"    # active gem-tile gradient bottom
CHIP_TOP = "#3358A0"    # active badge gradient top
CHIP_BOT = "#244179"    # active badge gradient bottom
CHIP_TX = "#DCE3F5"     # active badge label
RTILE_TOP = "#2C3358"   # retired gem-tile gradient top
RTILE_BOT = "#222845"   # retired gem-tile gradient bottom
RCHIP_TOP = "#2A3052"   # retired badge gradient top
RCHIP_BOT = "#212742"   # retired badge gradient bottom
RTX = "#8892B8"         # retired label + glyph + pill text
GOLD = "#B7995B"        # active glyph, accents, title sparkle
BLUE = "#3B6BB0"        # ambient glow
INK = "#C7D0E8"         # category names, title
INK_MUTED = "#7A88B8"   # subtitle, live label, guide line
FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,"
        "Arial,sans-serif")

# --- brand logos (simple-icons, 24x24 viewBox) -----------------------------
ICONS = {
    "langchain": "M13.796 0a6.93 6.93 0 0 0-4.91 2.019L5.451 5.455l3.273 3.27 3.432-3.432a2.284 2.284 0 0 1 3.277 0 2.28 2.28 0 0 1 0 3.275L12 12.001l3.273 3.273 3.433-3.435c2.692-2.692 2.692-7.127 0-9.82A6.92 6.92 0 0 0 13.796 0m-5.07 8.728-3.433 3.434c-2.692 2.693-2.692 7.126 0 9.819A6.92 6.92 0 0 0 10.203 24a6.93 6.93 0 0 0 4.911-2.02l3.432-3.432-3.271-3.272-3.433 3.433a2.284 2.284 0 0 1-3.277 0 2.28 2.28 0 0 1 0-3.276L12 12z",
    "langgraph": "M5 19H10A5 5 0 115 14ZM19 14A5 5 0 1114 19H19ZM10 5A5 5 0 105 10V5ZM19 5V10A5 5 0 1014 5Z",
    "openai": "M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z",
    "n8n": "M21.4737 5.6842c-1.1772 0-2.1663.8051-2.4468 1.8947h-2.8955c-1.235 0-2.289.893-2.492 2.111l-.1038.623a1.263 1.263 0 0 1-1.246 1.0555H11.289c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947s-2.1663.8051-2.4467 1.8947H4.973c-.2805-1.0896-1.2696-1.8947-2.4468-1.8947C1.1311 9.4737 0 10.6047 0 12s1.131 2.5263 2.5263 2.5263c1.1772 0 2.1663-.8051 2.4468-1.8947h1.4223c.2804 1.0896 1.2696 1.8947 2.4467 1.8947 1.1772 0 2.1663-.8051 2.4468-1.8947h1.0008a1.263 1.263 0 0 1 1.2459 1.0555l.1038.623c.203 1.218 1.257 2.111 2.492 2.111h.3692c.2804 1.0895 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263c-1.1772 0-2.1664.805-2.4468 1.8947h-.3692a1.263 1.263 0 0 1-1.246-1.0555l-.1037-.623A2.52 2.52 0 0 0 13.9607 12a2.52 2.52 0 0 0 .821-1.4794l.1038-.623a1.263 1.263 0 0 1 1.2459-1.0555h2.8955c.2805 1.0896 1.2696 1.8947 2.4468 1.8947 1.3952 0 2.5263-1.131 2.5263-2.5263s-1.131-2.5263-2.5263-2.5263m0 1.2632a1.263 1.263 0 0 1 1.2631 1.2631 1.263 1.263 0 0 1-1.2631 1.2632 1.263 1.263 0 0 1-1.2632-1.2632 1.263 1.263 0 0 1 1.2632-1.2631M2.5263 10.7368A1.263 1.263 0 0 1 3.7895 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 1.2632 12a1.263 1.263 0 0 1 1.2631-1.2632m6.3158 0A1.263 1.263 0 0 1 10.1053 12a1.263 1.263 0 0 1-1.2632 1.2632A1.263 1.263 0 0 1 7.579 12a1.263 1.263 0 0 1 1.2632-1.2632m10.1053 3.7895a1.263 1.263 0 0 1 1.2631 1.2632 1.263 1.263 0 0 1-1.2631 1.2631 1.263 1.263 0 0 1-1.2632-1.2631 1.263 1.263 0 0 1 1.2632-1.2632",
    "claude": "m4.7144 15.9555 4.7174-2.6471.079-.2307-.079-.1275h-.2307l-.7893-.0486-2.6956-.0729-2.3375-.0971-2.2646-.1214-.5707-.1215-.5343-.7042.0546-.3522.4797-.3218.686.0608 1.5179.1032 2.2767.1578 1.6514.0972 2.4468.255h.3886l.0546-.1579-.1336-.0971-.1032-.0972L6.973 9.8356l-2.55-1.6879-1.3356-.9714-.7225-.4918-.3643-.4614-.1578-1.0078.6557-.7225.8803.0607.2246.0607.8925.686 1.9064 1.4754 2.4893 1.8336.3643.3035.1457-.1032.0182-.0728-.164-.2733-1.3539-2.4467-1.445-2.4893-.6435-1.032-.17-.6194c-.0607-.255-.1032-.4674-.1032-.7285L6.287.1335 6.6997 0l.9957.1336.419.3642.6192 1.4147 1.0018 2.2282 1.5543 3.0296.4553.8985.2429.8318.091.255h.1579v-.1457l.1275-1.706.2368-2.0947.2307-2.6957.0789-.7589.3764-.9107.7468-.4918.5828.2793.4797.686-.0668.4433-.2853 1.8517-.5586 2.9021-.3643 1.9429h.2125l.2429-.2429.9835-1.3053 1.6514-2.0643.7286-.8196.85-.9046.5464-.4311h1.0321l.759 1.1293-.34 1.1657-1.0625 1.3478-.8804 1.1414-1.2628 1.7-.7893 1.36.0729.1093.1882-.0183 2.8535-.607 1.5421-.2794 1.8396-.3157.8318.3886.091.3946-.3278.8075-1.967.4857-2.3072.4614-3.4364.8136-.0425.0304.0486.0607 1.5482.1457.6618.0364h1.621l3.0175.2247.7892.522.4736.6376-.079.4857-1.2142.6193-1.6393-.3886-3.825-.9107-1.3113-.3279h-.1822v.1093l1.0929 1.0686 2.0035 1.8092 2.5075 2.3314.1275.5768-.3218.4554-.34-.0486-2.2039-1.6575-.85-.7468-1.9246-1.621h-.1275v.17l.4432.6496 2.3436 3.5214.1214 1.0807-.17.3521-.6071.2125-.6679-.1214-1.3721-1.9246L14.38 17.959l-1.1414-1.9428-.1397.079-.674 7.2552-.3156.3703-.7286.2793-.6071-.4614-.3218-.7468.3218-1.4753.3886-1.9246.3157-1.53.2853-1.9004.17-.6314-.0121-.0425-.1397.0182-1.4328 1.9672-2.1796 2.9446-1.7243 1.8456-.4128.164-.7164-.3704.0667-.6618.4008-.5889 2.386-3.0357 1.4389-1.882.929-1.0868-.0062-.1579h-.0546l-6.3385 4.1164-1.1293.1457-.4857-.4554.0608-.7467.2307-.2429 1.9064-1.3114Z",
    "kimi": "M21.765.351C22.998.351 24 1.353 24 2.586S22.998 4.82 21.765 4.82h-1.974c-.15 0-.26-.12-.26-.26V2.586A2.237 2.237 0 0 1 21.765.35M9.41 13.388l8.447-8.377c.16-.16.07-.471-.14-.471h-4.55s-.1.02-.14.06l-9.099 9.029c-.14.14-.35.02-.35-.21V4.81c0-.15-.1-.27-.221-.27H.22c-.12 0-.22.12-.22.27v18.57c0 .15.1.27.22.27h3.137c.12 0 .22-.12.22-.27v-3.79c0-.08.03-.16.08-.21l2.826-2.796c.07-.07.16-.08.241-.03l7.546 5.551a8.9 8.9 0 0 0 4.018 1.493c.12.01.23-.11.23-.27V19.76c0-.14-.08-.25-.19-.26a5.8 5.8 0 0 1-2.355-.942l-6.533-4.73c-.14-.09-.15-.32-.03-.441",
    "cline": "m23.365 13.556-1.442-2.895V8.994c0-2.764-2.218-5.002-4.954-5.002h-2.464c.178-.367.276-.779.276-1.213A2.77 2.77 0 0 0 12.018 0a2.77 2.77 0 0 0-2.763 2.779c0 .434.098.846.276 1.213H7.067c-2.736 0-4.954 2.238-4.954 5.002v1.667L.64 13.549c-.149.29-.149.636 0 .927l1.472 2.855v1.667C2.113 21.762 4.33 24 7.067 24h9.902c2.736 0 4.954-2.238 4.954-5.002V17.33l1.44-2.865c.143-.286.143-.622.002-.91m-12.854 2.36a2.27 2.27 0 0 1-2.261 2.273 2.27 2.27 0 0 1-2.261-2.273v-4.042A2.27 2.27 0 0 1 8.249 9.6a2.267 2.267 0 0 1 2.262 2.274zm7.285 0a2.27 2.27 0 0 1-2.26 2.273 2.27 2.27 0 0 1-2.262-2.273v-4.042A2.267 2.267 0 0 1 15.535 9.6a2.267 2.267 0 0 1 2.261 2.274z",
    "dify": "m22.417 9.334-1.333 4.333-1.334-4.333h-1.583L20.1 14.94c.2.583-.14 1.06-.756 1.06h-.678v1.334h.996c.869 0 1.65-.55 1.945-1.367L24 9.334ZM2.833 6.667H0v8.666h2.833c3.5 0 4.5-2 4.5-4.333s-1-4.334-4.5-4.334zM2.866 14H1.6V8h1.266c2.013 0 2.867.988 2.867 3s-.854 3-2.867 3m11-5.267v.6h-1.532v1.334h1.533V14h-2.534V9.334H8v1.334h1.867V14h-2.2v1.334h10V14h-2.332v-3.333h2.333V9.334h-2.333V8h2.333V6.667h-1.733a2.07 2.07 0 0 0-2.067 2.067Zm-3.266-.2c.681 0 .933-.417.933-.933 0-.515-.252-.933-.933-.933-.68 0-.934.418-.934.933s.253.934.934.934",
    "gemini": "M11.04 19.32Q12 21.51 12 24q0-2.49.93-4.68.96-2.19 2.58-3.81t3.81-2.55Q21.51 12 24 12q-2.49 0-4.68-.93a12.3 12.3 0 0 1-3.81-2.58 12.3 12.3 0 0 1-2.58-3.81Q12 2.49 12 0q0 2.49-.96 4.68-.93 2.19-2.55 3.81a12.3 12.3 0 0 1-3.81 2.58Q2.49 12 0 12q2.49 0 4.68.96 2.19.93 3.81 2.55t2.55 3.81",
}

SPARKLE = ("M12 0c.9 6.3 5.7 11.1 12 12-6.3.9-11.1 5.7-12 12"
           "-.9-6.3-5.7-11.1-12-12C6.3 11.1 11.1 6.3 12 0Z")

# (name, retired, category-glyph-key, [(label, brand-icon-key or None), ...])
ROWS = [
    ("Frameworks", False, "frameworks", [
        ("LangChain", "langchain"),
        ("LangGraph", "langgraph"),
        ("OpenAI SDK", "openai"),
    ]),
    ("Agents", False, "agents", [
        ("Claude Code", "claude"),
        ("Codex", "openai"),
        ("Kimi Code", "kimi"),
        ("Cline", "cline"),
        ("OpenCode", None),
        ("Pi", None),
        ("Druid", None),
        ("OpenClaw", None),
    ]),
    ("Retired", True, "retired", [
        ("Trae", None),
        ("Dify", None),
        ("Gemini CLI", "gemini"),
        ("Kimi CLI", "kimi"),
        ("n8n", "n8n"),
    ]),
]

# --- geometry ---------------------------------------------------------------
FS = 11          # badge label font-size
TITLE_FS = 18
SUB_FS = 9       # subtitle font-size
NAME_FS = 13     # category name font-size
STAT_FS = 9      # status pill font-size
L = 28           # left margin
R = 28           # right margin
TILE = 22        # category gem-tile size
GLYPH = 13       # glyph box inside a tile
ICON = 13        # brand-logo box inside a badge
ICON_GAP = 5     # gap between brand logo and label
BADGE_H = 22
RX = 4
PAD_X = 9        # horizontal padding inside a badge
BADGE_GAP = 8    # gap between badges in a row
WRAP_GAP = 8     # gap between wrapped lines within a category
ROW_GAP = 24     # gap between categories
ROW0 = 74        # first category top (title + subtitle sit above)
NAME_X = L + TILE + 9
NAME_W = 86      # reserved category-name column
CHIP_X = NAME_X + NAME_W + 14
STATUS_GAP = 14  # breathing room between badge flow and status pill
GUIDE_MIN = 12   # min gap before drawing the dashed guide line
W = 644          # fixed canvas width (wrapping keeps the dense rows inside it)


def char_w(ch):
    if ch == " ":
        return 3.6
    if ch in "iltfIj.'":
        return 3.7
    if ch in "mwMW":
        return 9.6
    if ch in "rs":
        return 5.2
    if ch.isupper():
        return 7.6
    if ch.isdigit():
        return 6.6
    return 6.3


def text_w(s, size=FS):
    return sum(char_w(c) for c in s) * size / 11.0


def badge_w(label, has_icon):
    w = PAD_X * 2 + text_w(label)
    if has_icon:
        w += ICON + ICON_GAP
    return w


def status_w(label):
    return 7 + 5 + 4 + text_w(label, STAT_FS) + 8


LIVE_W = status_w("LIVE")
RETIRED_W = status_w("RETIRED")
STATUS_RESERVE = max(LIVE_W, RETIRED_W)
STATUS_RIGHT = W - R
STATUS_LEFT = STATUS_RIGHT - STATUS_RESERVE
AVAIL1 = STATUS_LEFT - CHIP_X - STATUS_GAP   # first line yields to the pill
AVAILN = (W - R) - CHIP_X                    # continuation lines use full width


def wrap(items):
    """Greedy line-wrap of a badge list. First line is narrower (pill sits at
    its right edge); later lines use the full content width."""
    widths = [badge_w(lbl, ic is not None) for lbl, ic in items]
    lines, cur, cur_w = [], [], 0.0
    for it, bw in zip(items, widths):
        avail = AVAIL1 if not lines else AVAILN
        add = bw if not cur else bw + BADGE_GAP
        if cur and cur_w + add > avail:
            lines.append(cur)
            cur, cur_w = [], 0.0
            add = bw
        cur.append((it, bw))
        cur_w += add
    if cur:
        lines.append(cur)
    return lines, widths


def line_right(line):
    return sum(bw for _, bw in line) + BADGE_GAP * (len(line) - 1)


def cat_glyph(key, x, y, size, color):
    """Hand-drawn category mark in a 24x24 space, placed via transform."""
    s = size / 24.0
    if key == "frameworks":
        shapes = "".join(
            f'<rect x="{gx}" y="{gy}" width="9" height="9" rx="2" '
            f'fill="{color}"/>'
            for gx, gy in [(2, 2), (13, 2), (2, 13), (13, 13)]
        )
    elif key == "agents":
        shapes = f'<path d="{SPARKLE}" fill="{color}"/>'
    else:  # retired — archive box
        shapes = (
            f'<rect x="2" y="4" width="20" height="4" rx="1.5" fill="{color}"/>'
            f'<rect x="4" y="9" width="3" height="11" fill="{color}"/>'
            f'<rect x="17" y="9" width="3" height="11" fill="{color}"/>'
            f'<rect x="4" y="17" width="16" height="3" rx="1.5" fill="{color}"/>'
            f'<rect x="9" y="12" width="6" height="2" rx="1" fill="{color}"/>'
        )
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s:.4f})">'
            f'{shapes}</g>')


def status_pill(x, y, retired):
    w = RETIRED_W if retired else LIVE_W
    h = 18
    ty = y + (BADGE_H - h) / 2
    cy = ty + h / 2
    dot_cx = x + 7 + 2.5
    if retired:
        fill, stroke, dot_cls, dot_fill, tx = "#141B33", "#2A3052", "", RTX, RTX
        label = "RETIRED"
    else:
        fill, stroke, dot_cls, dot_fill, tx = BG, BORDER, "as-live", GOLD, INK_MUTED
        label = "LIVE"
    cls = f' class="{dot_cls}"' if dot_cls else ""
    return "\n".join([
        f'<rect x="{x:.1f}" y="{ty:.1f}" width="{w:.1f}" height="{h}" '
        f'rx="{RX}" fill="{fill}" stroke="{stroke}"/>',
        f'<circle{cls} cx="{dot_cx:.1f}" cy="{cy:.1f}" r="2.3" '
        f'fill="{dot_fill}"/>',
        f'<text x="{x + 16:.1f}" y="{cy + 3.2:.1f}" fill="{tx}" '
        f'font-size="{STAT_FS}" font-weight="700">{label}</text>',
    ])


def render():
    groups = []
    for name, retired, ckey, items in ROWS:
        lines, widths = wrap(items)
        groups.append((name, retired, ckey, items, lines, widths))

    group_tops, group_hs = [], []
    top = ROW0
    for *_rest, lines, _w in groups:
        group_tops.append(top)
        h = len(lines) * BADGE_H + (len(lines) - 1) * WRAP_GAP
        group_hs.append(h)
        top += h + ROW_GAP
    H = top - ROW_GAP + 20

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        "<defs>",
        '<radialGradient id="asGlow" cx="12%" cy="-10%" r="95%">',
        f'<stop offset="0%" stop-color="{BLUE}" stop-opacity="0.22"/>',
        f'<stop offset="55%" stop-color="{BLUE}" stop-opacity="0.05"/>',
        f'<stop offset="100%" stop-color="{BLUE}" stop-opacity="0"/>',
        "</radialGradient>",
        '<linearGradient id="asTop" x1="0" y1="0" x2="1" y2="0">',
        f'<stop offset="0%" stop-color="{GOLD}" stop-opacity="0"/>',
        f'<stop offset="50%" stop-color="{GOLD}" stop-opacity="0.6"/>',
        f'<stop offset="100%" stop-color="{GOLD}" stop-opacity="0"/>',
        "</linearGradient>",
        '<linearGradient id="asTile" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0%" stop-color="{TILE_TOP}"/>',
        f'<stop offset="100%" stop-color="{TILE_BOT}"/>',
        "</linearGradient>",
        '<linearGradient id="asChip" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0%" stop-color="{CHIP_TOP}"/>',
        f'<stop offset="100%" stop-color="{CHIP_BOT}"/>',
        "</linearGradient>",
        '<linearGradient id="asTileR" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0%" stop-color="{RTILE_TOP}"/>',
        f'<stop offset="100%" stop-color="{RTILE_BOT}"/>',
        "</linearGradient>",
        '<linearGradient id="asChipR" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0%" stop-color="{RCHIP_TOP}"/>',
        f'<stop offset="100%" stop-color="{RCHIP_BOT}"/>',
        "</linearGradient>",
        '<pattern id="asDots" width="22" height="22" patternUnits="userSpaceOnUse">',
        f'<circle cx="2" cy="2" r="0.7" fill="{INK}" opacity="0.05"/>',
        "</pattern>",
        '<clipPath id="asClip">'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6"/>'
        "</clipPath>",
        "</defs>",
        "<style>"
        "@keyframes asLive{0%,100%{opacity:1}50%{opacity:.5}}"
        ".as-live{animation:asLive 3.4s ease-in-out infinite}"
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        '<g clip-path="url(#asClip)">',
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#asDots)"/>',
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#asGlow)"/>',
        f'<rect x="1" y="1" width="{W-2}" height="1.5" fill="url(#asTop)"/>',
        "</g>",
    ]

    # title: gold sparkle + name + tracked subtitle
    out.append(
        f'<g transform="translate({L},19) scale({16/24:.4f})">'
        f'<path d="{SPARKLE}" fill="{GOLD}"/></g>'
    )
    out.append(
        f'<text x="{L+24}" y="35" fill="{INK}" font-size="{TITLE_FS}" '
        f'font-weight="600">The Fleet</text>'
    )
    out.append(
        f'<text x="{L+24}" y="51" fill="{INK_MUTED}" font-size="{SUB_FS}" '
        f'font-weight="600" letter-spacing="1.4">'
        f'FRAMEWORKS · AGENTS · RETIRED</text>'
    )

    for (name, retired, ckey, items, lines, widths), gtop, gh in \
            zip(groups, group_tops, group_hs):
        tile_fill = "url(#asTileR)" if retired else "url(#asTile)"
        glyph_c = RTX if retired else GOLD
        name_c = RTX if retired else INK
        # left column: gem tile + category name, anchored to the first line so
        # the row reads exactly like a model-fleet row; wrapped continuation
        # lines below are graceful overflow (left + right whitespace).
        tile_y = gtop
        out.append(
            f'<rect x="{L}" y="{tile_y:.1f}" width="{TILE}" height="{TILE}" '
            f'rx="5" fill="{tile_fill}"/>'
        )
        out.append(
            f'<rect x="{L+2}" y="{tile_y+1.5:.1f}" width="{TILE-4}" '
            f'height="1" rx="0.5" fill="#FFFFFF" opacity="0.10"/>'
        )
        gg = (TILE - GLYPH) / 2
        out.append(cat_glyph(ckey, L + gg, tile_y + gg, GLYPH, glyph_c))
        out.append(
            f'<text x="{NAME_X}" y="{tile_y + TILE/2 + 4.5:.1f}" '
            f'fill="{name_c}" font-size="{NAME_FS}" '
            f'font-weight="600">{name}</text>'
        )

        # right column: wrapped badge flow
        for li, line in enumerate(lines):
            by = gtop + li * (BADGE_H + WRAP_GAP)
            cy = by + BADGE_H / 2
            x = CHIP_X
            for (lbl, ic), bw in line:
                chip_fill = "url(#asChipR)" if retired else "url(#asChip)"
                hi_op = "0.05" if retired else "0.10"
                tx_c = RTX if retired else CHIP_TX
                ic_c = RTX if retired else GOLD
                out.append(
                    f'<rect x="{x:.1f}" y="{by:.1f}" width="{bw:.1f}" '
                    f'height="{BADGE_H}" rx="{RX}" fill="{chip_fill}"/>'
                )
                out.append(
                    f'<rect x="{x+1.5:.1f}" y="{by+1.5:.1f}" '
                    f'width="{bw-3:.1f}" height="1" rx="0.5" '
                    f'fill="#FFFFFF" opacity="{hi_op}"/>'
                )
                inner = x + PAD_X
                if ic:
                    iy = by + (BADGE_H - ICON) / 2
                    out.append(
                        f'<g transform="translate({inner:.1f},{iy:.1f}) '
                        f'scale({ICON/24:.4f})"><path d="{ICONS[ic]}" '
                        f'fill="{ic_c}"/></g>'
                    )
                    inner += ICON + ICON_GAP
                out.append(
                    f'<text x="{inner:.1f}" y="{cy + 3.7:.1f}" fill="{tx_c}" '
                    f'font-size="{FS}" font-weight="500">{lbl}</text>'
                )
                x += bw + BADGE_GAP
            right = x - BADGE_GAP
            # first line: dashed guide to the status pill (if room)
            if li == 0:
                sw = RETIRED_W if retired else LIVE_W
                pill_x = STATUS_RIGHT - sw
                g1, g2 = right + 8, pill_x - 8
                if g2 - g1 >= GUIDE_MIN:
                    out.append(
                        f'<line x1="{g1:.1f}" y1="{cy:.1f}" x2="{g2:.1f}" '
                        f'y2="{cy:.1f}" stroke="{INK_MUTED}" stroke-width="1" '
                        f'stroke-dasharray="2 4" opacity="0.28"/>'
                    )
                out.append(status_pill(pill_x, by, retired))

    out.append("</svg>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/agent-stack.svg")
    add_backup_args(ap)
    args = ap.parse_args()

    missing = [ic for *_r, items in ROWS for _l, ic in items
               if ic and ic not in ICONS]
    if missing:
        sys.exit(f"no icon path for: {', '.join(sorted(set(missing)))}")

    svg = render()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg + "\n")
    n = sum(len(items) for *_r, items in ROWS)
    print(f"wrote {args.out}: {len(ROWS)} categories, {n} badges")
    maybe_snapshot(args)


if __name__ == "__main__":
    main()
