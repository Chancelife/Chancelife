#!/usr/bin/env python3
"""Generate a static, self-contained "Model Arsenal" card SVG.

Renders the supported-model matrix (provider x models) in the lapis theme as a
bordered card with brand glyphs inlined as vector paths — zero external runtime
dependency, same static-by-design pattern as gen-stats-card.py /
gen-agent-stack.py.

Static by design: edit PROVIDERS below and re-run to refresh.

    python scripts/gen-model-fleet.py

Provider glyphs: claude / kimi / openai from simple-icons (CC0-1.0, 24x24
viewBox); qwen is a hand-drawn four-point sparkle mark.

Visual layering (the card is embedded via README <img>, so CSS keyframes work
but external web fonts do NOT load — the system-font stack is intentional and
the type hierarchy is carried by size / weight / tracking instead):
  * starfield pattern + radial glow  -> ambient depth
  * gold top-edge highlight          -> brushed-metal frame
  * vertical-gradient tiles & chips  -> inset gem / raised pill
  * right-aligned per-row status     -> LIVE (soft pulse) / NEW (gold, fast pulse)
  * dashed guide line                -> ties sparse rows to their status
  * gold marching-ants on Qwen chip  -> "just onboarded" liveness
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _backup import add_backup_args, maybe_snapshot  # noqa: E402

# --- lapis theme (shared with gen-stats-card.py / gen-agent-stack.py) -------
BG = "#0A1633"          # card surface
BORDER = "#1E2A54"      # card border / live-pill stroke
TILE_TOP = "#34599F"    # provider tile gradient top
TILE_BOT = "#21407A"    # provider tile gradient bottom
CHIP_TOP = "#3358A0"    # model chip gradient top
CHIP_BOT = "#244179"    # model chip gradient bottom
CHIP_TX = "#DCE3F5"     # model chip label
GOLD = "#B7995B"        # glyphs, accents, NEW badge
GOLD_HI = "#E6CF94"     # marching-ants highlight
BLUE = "#3B6BB0"        # ambient glow
INK = "#C7D0E8"         # provider names, title
INK_MUTED = "#7A88B8"   # subtitle, live label, guide line
FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,"
        "Arial,sans-serif")

# --- provider glyphs (24x24 viewBox) ----------------------------------------
ICONS = {
    "claude": "m4.7144 15.9555 4.7174-2.6471.079-.2307-.079-.1275h-.2307l-.7893-.0486-2.6956-.0729-2.3375-.0971-2.2646-.1214-.5707-.1215-.5343-.7042.0546-.3522.4797-.3218.686.0608 1.5179.1032 2.2767.1578 1.6514.0972 2.4468.255h.3886l.0546-.1579-.1336-.0971-.1032-.0972L6.973 9.8356l-2.55-1.6879-1.3356-.9714-.7225-.4918-.3643-.4614-.1578-1.0078.6557-.7225.8803.0607.2246.0607.8925.686 1.9064 1.4754 2.4893 1.8336.3643.3035.1457-.1032.0182-.0728-.164-.2733-1.3539-2.4467-1.445-2.4893-.6435-1.032-.17-.6194c-.0607-.255-.1032-.4674-.1032-.7285L6.287.1335 6.6997 0l.9957.1336.419.3642.6192 1.4147 1.0018 2.2282 1.5543 3.0296.4553.8985.2429.8318.091.255h.1579v-.1457l.1275-1.706.2368-2.0947.2307-2.6957.0789-.7589.3764-.9107.7468-.4918.5828.2793.4797.686-.0668.4433-.2853 1.8517-.5586 2.9021-.3643 1.9429h.2125l.2429-.2429.9835-1.3053 1.6514-2.0643.7286-.8196.85-.9046.5464-.4311h1.0321l.759 1.1293-.34 1.1657-1.0625 1.3478-.8804 1.1414-1.2628 1.7-.7893 1.36.0729.1093.1882-.0183 2.8535-.607 1.5421-.2794 1.8396-.3157.8318.3886.091.3946-.3278.8075-1.967.4857-2.3072.4614-3.4364.8136-.0425.0304.0486.0607 1.5482.1457.6618.0364h1.621l3.0175.2247.7892.522.4736.6376-.079.4857-1.2142.6193-1.6393-.3886-3.825-.9107-1.3113-.3279h-.1822v.1093l1.0929 1.0686 2.0035 1.8092 2.5075 2.3314.1275.5768-.3218.4554-.34-.0486-2.2039-1.6575-.85-.7468-1.9246-1.621h-.1275v.17l.4432.6496 2.3436 3.5214.1214 1.0807-.17.3521-.6071.2125-.6679-.1214-1.3721-1.9246L14.38 17.959l-1.1414-1.9428-.1397.079-.674 7.2552-.3156.3703-.7286.2793-.6071-.4614-.3218-.7468.3218-1.4753.3886-1.9246.3157-1.53.2853-1.9004.17-.6314-.0121-.0425-.1397.0182-1.4328 1.9672-2.1796 2.9446-1.7243 1.8456-.4128.164-.7164-.3704.0667-.6618.4008-.5889 2.386-3.0357 1.4389-1.882.929-1.0868-.0062-.1579h-.0546l-6.3385 4.1164-1.1293.1457-.4857-.4554.0608-.7467.2307-.2429 1.9064-1.3114Z",
    "kimi": "M21.765.351C22.998.351 24 1.353 24 2.586S22.998 4.82 21.765 4.82h-1.974c-.15 0-.26-.12-.26-.26V2.586A2.237 2.237 0 0 1 21.765.35M9.41 13.388l8.447-8.377c.16-.16.07-.471-.14-.471h-4.55s-.1.02-.14.06l-9.099 9.029c-.14.14-.35.02-.35-.21V4.81c0-.15-.1-.27-.221-.27H.22c-.12 0-.22.12-.22.27v18.57c0 .15.1.27.22.27h3.137c.12 0 .22-.12.22-.27v-3.79c0-.08.03-.16.08-.21l2.826-2.796c.07-.07.16-.08.241-.03l7.546 5.551a8.9 8.9 0 0 0 4.018 1.493c.12.01.23-.11.23-.27V19.76c0-.14-.08-.25-.19-.26a5.8 5.8 0 0 1-2.355-.942l-6.533-4.73c-.14-.09-.15-.32-.03-.441",
    "openai": "M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z",
    # hand-drawn four-point sparkle (Qwen has no simple-icons glyph)
    "qwen": "M12 0c.9 6.3 5.7 11.1 12 12-6.3.9-11.1 5.7-12 12-.9-6.3-5.7-11.1-12-12C6.3 11.1 11.1 6.3 12 0Z",
}

# Provider rows, top to bottom. `new` flips the row's chips to gold-outline
# style with a marching-ants highlight and gives it a gold NEW status pill
# (plan just purchased, first test sessions).
PROVIDERS = [
    {"name": "Anthropic", "icon": "claude",
     "models": ["Sonnet 4.8", "Sonnet 5", "Claude 4.8", "Claude 5"]},
    {"name": "Kimi", "icon": "kimi",
     "models": ["Kimi 2.7", "Kimi 2.7 High Speed"]},
    {"name": "OpenAI", "icon": "openai",
     "models": ["GPT 5.5", "GPT 5.6 Sol", "GPT 5.6 Terra"]},
    {"name": "Qwen", "icon": "qwen", "new": True,
     "models": ["首批测试"]},
]

# --- geometry ---------------------------------------------------------------
FS = 11          # chip label font-size
TITLE_FS = 18
SUB_FS = 9       # subtitle font-size
NAME_FS = 13     # provider name font-size
STAT_FS = 9      # status pill font-size
L = 28           # left margin
R = 28           # right margin
TILE = 22        # provider tile size
GLYPH = 13       # glyph box inside a tile
CHIP_H = 22
RX = 4
PAD_X = 9        # horizontal padding inside a chip / pill
CHIP_GAP = 8     # gap between chips
ROW0 = 74        # first row top (title + subtitle sit above)
STEP = 34        # row pitch
NAME_X = L + TILE + 9
NAME_W = 78      # reserved provider-name column
CHIP_X = NAME_X + NAME_W + 14
STATUS_GAP = 14  # min breathing room between chip row and status pill
GUIDE_MIN = 18   # only draw the guide line when the gap exceeds this


def char_w(ch):
    if ord(ch) > 0x2E7F:      # CJK & friends: full-width
        return 11.5
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


def chip_w(label):
    return PAD_X * 2 + text_w(label)


def status_w(label):
    return 7 + 5 + 4 + text_w(label, STAT_FS) + 8


LIVE_W = status_w("LIVE")
NEW_W = status_w("NEW")
STATUS_RESERVE = max(LIVE_W, NEW_W)


def render():
    max_chip_right = 0
    for p in PROVIDERS:
        end = CHIP_X + sum(chip_w(m) for m in p["models"]) \
            + CHIP_GAP * (len(p["models"]) - 1)
        max_chip_right = max(max_chip_right, end)

    W = int(round(max_chip_right + STATUS_GAP + STATUS_RESERVE + R))
    H = ROW0 + STEP * (len(PROVIDERS) - 1) + TILE + 20
    status_right = W - R

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        "<defs>",
        '<radialGradient id="mfGlow" cx="12%" cy="-10%" r="95%">',
        f'<stop offset="0%" stop-color="{BLUE}" stop-opacity="0.22"/>',
        f'<stop offset="55%" stop-color="{BLUE}" stop-opacity="0.05"/>',
        f'<stop offset="100%" stop-color="{BLUE}" stop-opacity="0"/>',
        "</radialGradient>",
        '<linearGradient id="mfTop" x1="0" y1="0" x2="1" y2="0">',
        f'<stop offset="0%" stop-color="{GOLD}" stop-opacity="0"/>',
        f'<stop offset="50%" stop-color="{GOLD}" stop-opacity="0.6"/>',
        f'<stop offset="100%" stop-color="{GOLD}" stop-opacity="0"/>',
        "</linearGradient>",
        '<linearGradient id="mfTile" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0%" stop-color="{TILE_TOP}"/>',
        f'<stop offset="100%" stop-color="{TILE_BOT}"/>',
        "</linearGradient>",
        '<linearGradient id="mfChip" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0%" stop-color="{CHIP_TOP}"/>',
        f'<stop offset="100%" stop-color="{CHIP_BOT}"/>',
        "</linearGradient>",
        '<pattern id="mfDots" width="22" height="22" patternUnits="userSpaceOnUse">',
        f'<circle cx="2" cy="2" r="0.7" fill="{INK}" opacity="0.05"/>',
        "</pattern>",
        '<clipPath id="mfClip">'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6"/>'
        "</clipPath>",
        "</defs>",
        "<style>"
        "@keyframes mfPulse{0%,100%{opacity:1}50%{opacity:.15}}"
        "@keyframes mfLive{0%,100%{opacity:1}50%{opacity:.5}}"
        "@keyframes mfFlow{to{stroke-dashoffset:-24}}"
        ".mf-pulse{animation:mfPulse 2.2s ease-in-out infinite}"
        ".mf-live{animation:mfLive 3.4s ease-in-out infinite}"
        ".mf-flow{animation:mfFlow 2.6s linear infinite}"
        "</style>",
        # base surface
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="6" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # clipped ambient layers
        '<g clip-path="url(#mfClip)">',
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#mfDots)"/>',
        f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#mfGlow)"/>',
        f'<rect x="1" y="1" width="{W-2}" height="1.5" fill="url(#mfTop)"/>',
        "</g>",
    ]

    # title: gold sparkle + name + tracked subtitle
    out.append(
        f'<g transform="translate({L},19) scale({16/24:.4f})">'
        f'<path d="{ICONS["qwen"]}" fill="{GOLD}"/></g>'
    )
    out.append(
        f'<text x="{L+24}" y="35" fill="{INK}" font-size="{TITLE_FS}" '
        f'font-weight="600">Model Arsenal</text>'
    )
    out.append(
        f'<text x="{L+24}" y="51" fill="{INK_MUTED}" font-size="{SUB_FS}" '
        f'font-weight="600" letter-spacing="1.4">'
        f'BRING YOUR OWN MODEL · LIVE FLEET</text>'
    )

    for i, p in enumerate(PROVIDERS):
        y = ROW0 + i * STEP
        new = p.get("new", False)
        cy = y + CHIP_H / 2

        # provider tile (gem) + top highlight + glyph
        out.append(
            f'<rect x="{L}" y="{y}" width="{TILE}" height="{TILE}" rx="5" '
            f'fill="url(#mfTile)"/>'
        )
        out.append(
            f'<rect x="{L+2}" y="{y+1.5}" width="{TILE-4}" height="1" '
            f'rx="0.5" fill="#FFFFFF" opacity="0.14"/>'
        )
        g = (TILE - GLYPH) / 2
        out.append(
            f'<g transform="translate({L+g:.1f},{y+g:.1f}) '
            f'scale({GLYPH/24:.4f})"><path d="{ICONS[p["icon"]]}" '
            f'fill="{GOLD}"/></g>'
        )
        # provider name
        out.append(
            f'<text x="{NAME_X}" y="{cy + 4.5:.1f}" fill="{INK}" '
            f'font-size="{NAME_FS}" font-weight="600">{p["name"]}</text>'
        )
        # model chips
        x = CHIP_X
        for m in p["models"]:
            cw = chip_w(m)
            if new:
                out.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" '
                    f'height="{CHIP_H}" rx="{RX}" fill="{BG}" '
                    f'stroke="{GOLD}"/>'
                )
                out.append(
                    f'<rect class="mf-flow" x="{x:.1f}" y="{y:.1f}" '
                    f'width="{cw:.1f}" height="{CHIP_H}" rx="{RX}" '
                    f'fill="none" stroke="{GOLD_HI}" stroke-width="1" '
                    f'stroke-dasharray="4 8"/>'
                )
                tx_c = GOLD
            else:
                out.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" '
                    f'height="{CHIP_H}" rx="{RX}" fill="url(#mfChip)"/>'
                )
                out.append(
                    f'<rect x="{x+1.5:.1f}" y="{y+1.5:.1f}" '
                    f'width="{cw-3:.1f}" height="1" rx="0.5" '
                    f'fill="#FFFFFF" opacity="0.10"/>'
                )
                tx_c = CHIP_TX
            out.append(
                f'<text x="{x + PAD_X:.1f}" y="{cy + 3.7:.1f}" '
                f'fill="{tx_c}" font-size="{FS}" font-weight="500">{m}</text>'
            )
            x += cw + CHIP_GAP
        chip_right = x - CHIP_GAP

        # right-aligned status pill
        sw = NEW_W if new else LIVE_W
        sx = status_right - sw
        guide_x1 = chip_right + 8
        guide_x2 = sx - 8
        if guide_x2 - guide_x1 >= GUIDE_MIN:
            out.append(
                f'<line x1="{guide_x1:.1f}" y1="{cy:.1f}" '
                f'x2="{guide_x2:.1f}" y2="{cy:.1f}" stroke="{INK_MUTED}" '
                f'stroke-width="1" stroke-dasharray="2 4" opacity="0.28"/>'
            )
        out.append(status_pill(sx, y, new))

    out.append("</svg>")
    return "\n".join(out)


def status_pill(x, y, new):
    """Right-aligned status pill: gold NEW (fast pulse) or bordered LIVE
    (soft pulse)."""
    w = NEW_W if new else LIVE_W
    h = 18
    ty = y + (CHIP_H - h) / 2
    cy = ty + h / 2
    dot_cx = x + 7 + 2.5
    if new:
        fill, stroke, dot_cls, tx = GOLD, GOLD, "mf-pulse", BG
        label = "NEW"
    else:
        fill, stroke, dot_cls, tx = BG, BORDER, "mf-live", INK_MUTED
        label = "LIVE"
    dot_fill = BG if new else GOLD
    parts = [
        f'<rect x="{x:.1f}" y="{ty:.1f}" width="{w:.1f}" height="{h}" '
        f'rx="{RX}" fill="{fill}" stroke="{stroke}"/>',
        f'<circle class="{dot_cls}" cx="{dot_cx:.1f}" cy="{cy:.1f}" r="2.3" '
        f'fill="{dot_fill}"/>',
        f'<text x="{x + 16:.1f}" y="{cy + 3.2:.1f}" fill="{tx}" '
        f'font-size="{STAT_FS}" font-weight="700">{label}</text>',
    ]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets/model-fleet.svg")
    add_backup_args(ap)
    args = ap.parse_args()

    missing = [p["icon"] for p in PROVIDERS if p["icon"] not in ICONS]
    if missing:
        sys.exit(f"no icon path for: {', '.join(missing)}")

    svg = render()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg + "\n")
    n = sum(len(p["models"]) for p in PROVIDERS)
    print(f"wrote {args.out}: {len(PROVIDERS)} providers, {n} models")
    maybe_snapshot(args)


if __name__ == "__main__":
    main()
