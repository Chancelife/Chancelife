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
Qoder's two-tone mark is from lobe-icons (github.com/lobehub/lobe-icons), MIT.
An ICONS value is either one path string, or a list of (path, opacity) layers.
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
    "qoder": [
        ("M23.376 14.458v-4.056c0-2.304-1.003-4.154-2.748-5.075L11.612.574l-.046.086-.045.086c1.68.886 2.644 2.673 2.644 4.902v4.056a7.928 7.928 0 01-.014.454l-.005.061c-.005.081-.01.164-.018.245a4.897 4.897 0 01-.011.1l-.01.076c-.008.068-.015.135-.025.203l-.018.113-.01.058a9.99 9.99 0 01-.098.513l-.007.03a7.209 7.209 0 01-.074.294l-.024.086c-.027.099-.056.197-.087.296l-.027.085a9.592 9.592 0 01-.111.323l-.033.085-.018.046c-.032.082-.064.166-.098.248-.019.048-.04.096-.061.145l-.007.017a6 6 0 01-.084.187c-.024.056-.05.11-.077.165-.03.061-.058.122-.089.182a9.423 9.423 0 01-.176.332c-.03.056-.062.111-.094.167-.031.053-.062.108-.095.16-.033.055-.066.11-.101.164-.033.053-.065.104-.1.155-.034.055-.07.107-.111.169l-.099.144a15.193 15.193 0 01-.34.457c-.04.05-.08.102-.121.151l-.107.128-.007.008a6.987 6.987 0 01-.262.298l-.149.16-.116.12a9.562 9.562 0 01-.204.198l-.03.03-.072.069a9.05 9.05 0 01-.263.235l-.025.022-.029.026-.042.035a11.7 11.7 0 01-.22.18l-.07.055-.018.013a8.904 8.904 0 01-.194.146c-.029.02-.057.042-.086.063a7.7 7.7 0 01-.22.152l-.057.04a8.865 8.865 0 01-.293.185l-.062.037a10.424 10.424 0 01-.307.173l-.037.02-.196.103-.108.052-.012.006a6.196 6.196 0 01-.315.143c-.065.028-.13.054-.196.08l-.035.014-.086.034c-.07.026-.143.05-.215.075l-.039.014-.064.023a8.056 8.056 0 01-.323.097l-.63.173a7.285 7.285 0 01-.33.08l-.07.015c-.053.012-.104.023-.157.032l-.065.011-.085.015a2.332 2.332 0 01-.194.027l-.085.01a4.715 4.715 0 01-.16.018l-.034.003a4.861 4.861 0 01-.246.016h-.033a2.714 2.714 0 01-.155.005h-.106a3.384 3.384 0 01-.225-.007H4.86l-.15-.012-.066-.006a5.586 5.586 0 01-.187-.02l-.04-.005a5.14 5.14 0 01-.219-.035l-.054-.01a6.943 6.943 0 01-.347-.082l-.03-.008-.038-.01a5.034 5.034 0 01-.269-.086l-.063-.023a4.216 4.216 0 01-.188-.073l-.071-.031-.016-.007a4.959 4.959 0 01-.16-.074l-.026-.013a.164.164 0 00-.014-.007l-.671-.351.486.486h.016l8.995 4.742.093.048.03.014.02.01c.056.026.111.052.169.076l.016.008.073.032.195.076.022.008a.718.718 0 01.03.012l.014.004a4.693 4.693 0 00.323.1l.027.007c.073.02.147.038.22.055l.018.004.027.006.066.013.088.016c.075.014.15.026.226.038l.042.004c.064.009.128.016.193.022l.126.012.06.003.05.002.098.005c.046.002.094.002.14.003h.12c.05 0 .1-.002.161-.005h.033l.07-.004a6.17 6.17 0 00.184-.014l.033-.003a.753.753 0 00.058-.005l.108-.012.081-.01.08-.01.129-.021.082-.014.071-.012c.054-.01.107-.021.16-.033l.066-.013.059-.013c.096-.022.192-.046.287-.073l.63-.172a7.354 7.354 0 00.397-.122l.04-.015c.075-.025.149-.051.222-.078.032-.011.062-.024.093-.037l.03-.012c.067-.027.135-.054.2-.082l.128-.056.195-.09.021-.01.102-.05c.068-.034.135-.069.202-.105l.037-.02.073-.038c.08-.044.16-.092.24-.139l.026-.015a8.086 8.086 0 00.322-.2l.065-.045 1.98.902a1.748 1.748 0 002.472-1.59v-7.33l.004.004z", 0.5),
        ("M11.617.576a3.904 3.904 0 00-.093-.047c-.016-.009-.033-.016-.05-.024a5.854 5.854 0 00-.166-.077l-.09-.04a4.094 4.094 0 00-.194-.074c-.017-.006-.035-.015-.053-.02l-.013-.005a5.18 5.18 0 00-.277-.088l-.07-.019a4.034 4.034 0 00-.219-.053c-.015-.003-.03-.008-.044-.012L10.253.1l-.057-.011a5.177 5.177 0 00-.225-.036L9.928.047a5.972 5.972 0 00-.191-.022L9.669.02a1.33 1.33 0 00-.058-.005L9.515.009a4.058 4.058 0 00-.111-.005C9.354 0 9.304 0 9.254 0h-.109c-.052 0-.106.004-.16.004L8.884.01A5.32 5.32 0 008.7.022l-.083.006h-.008c-.05.005-.1.013-.15.019l-.12.014c-.056.008-.112.018-.169.028-.037.006-.074.011-.11.018a7.054 7.054 0 00-.572.133l-.63.172c-.111.031-.22.064-.33.1-.037.011-.072.025-.108.037a12.91 12.91 0 00-.345.126c-.067.027-.133.054-.2.083l-.128.055a11.916 11.916 0 00-.318.15 7.376 7.376 0 00-.311.163c-.082.045-.16.092-.24.14a9.424 9.424 0 00-.35.218l-.016.01-.06.04a9.242 9.242 0 00-.51.37 12.54 12.54 0 00-.315.254l-.043.034-.01.007-.045.041c-.09.078-.18.158-.268.24l-.106.101c-.07.067-.139.135-.207.204l-.056.054-.063.067-.153.164-.12.133-.148.17c-.024.03-.049.057-.073.086l-.043.053a5.96 5.96 0 00-.123.155l-.118.151c-.04.053-.08.106-.118.16l-.075.101-.038.056-.107.155-.11.164a9.91 9.91 0 00-.168.265c-.012.02-.023.043-.037.063a12.43 12.43 0 00-.192.335l-.09.168c-.019.034-.04.07-.057.105-.011.022-.02.043-.032.065l-.092.188-.08.167a19.15 19.15 0 00-.083.192c-.017.038-.035.076-.05.115-.008.016-.014.034-.021.051-.035.083-.067.167-.1.253l-.051.134c-.04.11-.077.22-.113.33l-.02.057c0 .002 0 .005-.002.007l-.008.026c-.032.1-.06.2-.09.301l-.023.089c-.027.1-.052.2-.075.301l-.007.03a7.63 7.63 0 00-.057.267l-.008.048c-.015.074-.026.148-.038.223L.082 8.4c-.011.078-.02.156-.029.234-.006.051-.013.103-.017.154a6.57 6.57 0 00-.02.26c-.003.044-.007.086-.009.13-.004.128-.007.257-.007.386v4.056c0 1.478.42 2.741 1.138 3.692A4.75 4.75 0 002.73 18.67l9.015 4.753c-1.656-.874-2.728-2.685-2.73-5.051v-4.056c0-.13.004-.26.01-.39.002-.043.006-.085.01-.128.005-.088.01-.174.019-.261l.017-.155c.01-.077.018-.155.029-.234l.026-.164c.013-.074.025-.15.039-.223.02-.105.04-.21.064-.313l.008-.031c.023-.1.048-.201.075-.301l.023-.088c.028-.1.058-.202.09-.302l.008-.025.021-.063c.036-.11.073-.22.113-.33l.052-.134c.031-.085.065-.169.1-.253.022-.056.047-.111.07-.166a13.856 13.856 0 01.164-.358c.03-.063.06-.126.092-.188l.088-.172a9.22 9.22 0 01.187-.338l.096-.164c.034-.057.069-.112.104-.168l.1-.159a10.49 10.49 0 01.567-.786l.123-.155.116-.139c.05-.057.098-.115.148-.171a14.092 14.092 0 01.272-.297 9.706 9.706 0 01.432-.425c.088-.083.177-.163.268-.241l.054-.048a10.08 10.08 0 01.553-.435l.092-.068c.075-.053.15-.105.226-.156.019-.013.038-.028.06-.04a9.18 9.18 0 01.362-.227c.08-.047.16-.094.241-.139l.11-.058a7.643 7.643 0 01.521-.256l.126-.056a7.509 7.509 0 01.546-.208l.107-.037c.11-.036.22-.069.33-.1l.63-.172c.095-.026.191-.05.287-.072l.097-.02c.062-.014.125-.029.187-.04l.114-.018c.055-.01.11-.02.166-.028.04-.006.08-.01.12-.014.053-.007.105-.014.157-.019l.083-.006c.061-.005.123-.01.184-.013.034-.003.067-.003.101-.004l.16-.006h.11a3.187 3.187 0 01.261.008l.153.01.067.007c.064.006.128.013.192.022l.043.005a5.232 5.232 0 01.281.047l.141.03c.073.016.146.035.218.053l.07.019c.094.026.187.055.278.087l.067.025a4.326 4.326 0 01.449.19l.143.072L11.617.576z", 1),
    ],
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
        ("Qoder", "qoder"),
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


def icon_paths(key, color):
    """One or more <path>s for a brand logo (multi-layer icons keep opacity)."""
    icon = ICONS[key]
    if isinstance(icon, str):
        icon = [(icon, 1)]
    return "".join(
        f'<path d="{d}" fill="{color}"'
        + (f' opacity="{op}"' if op != 1 else "") + "/>"
        for d, op in icon
    )


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
                        f'scale({ICON/24:.4f})">{icon_paths(ic, ic_c)}</g>'
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
