"""Draw the 25 November 2026 one-page newspaper for make.fun, round 7.

Renders a 1024x1024 broadsheet front page with 50 verified stories:
1 hero + 2 medium + 3 small + 36 IN BRIEF + 8 ticker items.
The density push: briefs move to three columns at 11pt so 10 new
stories fit without squeezing the hero, medium or small boxes.
Deterministic: no network, no clock, no randomness -- every run
writes the same bytes. Run: python3 draw.py  (writes entry.png)
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968 content width

PAPER = (253, 246, 233)
INK = (26, 26, 26)
RED = (163, 22, 33)
BLUE = (29, 53, 87)
GOLD = (150, 105, 20)
GREY = (90, 86, 78)
TICKER_BG = (26, 26, 26)
TICKER_FG = (253, 246, 233)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _load(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: _load("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: _load("DejaVuSans.ttf", s)
SANS_B = lambda s: _load("DejaVuSans-Bold.ttf", s)

# ---------------------------------------------------------------- stories
# Every item below was verified against a real dated source for 24-25 Nov
# 2026 (Reuters / AP / BBC / Al Jazeera / Dawn / Xinhua / FT / Censor.net /
# Kyiv Independent / Ukrinform / CNA / WHO / ICBL / CAS / UEFA).
# The SMALL Gaza slot stays the Tuesday 24 Nov seven-kill event
# (Abu Nahal + 3 + 3 = 7, Dawn/Straits Times); Wednesday's seven includes
# the Shati family already covered by the SHATI brief -- no double-count.

HERO = {
    "kicker": "SPACE  •  TOP STORY",
    "headline": "PAKISTAN'S FIRST ASTRONAUT REACHES ORBIT",
    "body": ("China's Shenzhou-24 blasted off from Jiuquan at 00:18 UTC with "
             "Tang Hongbo, Wu Yi and Pakistan's Muhammad Zeeshan Ali - the "
             "first Pakistani in orbit and the first foreigner to board "
             "Tiangong. The craft docked 3 hours 38 minutes later; Ali will "
             "spend about a week on experiments in orbit."),
}

MEDIUM = [
    {
        "kicker": "YEMEN  •  RED SEA",
        "headline": "HOUTHIS CLAIM STRIKES ON SAUDI PORTS",
        "body": ("Yemen's Houthis claim strikes on Jeddah and Jazan ports, "
                 "saying a projectile hit Jazan, and say they hit the Ras "
                 "Tanura refinery. The Saudi-led coalition struck back "
                 "at Hodeidah."),
    },
    {
        "kicker": "PACIFIC  •  TREATY",
        "headline": "SOLOMONS SIGNS AUSTRALIA SECURITY PACT",
        "body": ("Australia and Solomon Islands signed a treaty in Canberra "
                 "making Canberra the islands' primary security partner, "
                 "with no foreign military base on its soil. Australia "
                 "pledges A$740m over a decade."),
    },
]

SMALL = [
    {
        "kicker": "GAZA",
        "headline": "ISRAELI STRIKES KILL SEVEN ACROSS GAZA",
        "body": ("Seven Palestinians killed in Israeli strikes across Gaza "
                 "on Tuesday; 1,679 dead since the October 2025 ceasefire."),
    },
    {
        "kicker": "UNITED STATES",
        "headline": "ABREGO GARCIA LEAVES US FOR SPAIN",
        "body": ("The Salvadoran migrant wrongfully deported to El Salvador "
                 "leaves the US voluntarily, ending a 20-month legal "
                 "fight."),
    },
    {
        "kicker": "TRADE",
        "headline": "US PROPOSES NEW TARIFFS ON 14 PARTNERS",
        "body": ("The Trump administration proposes Section 301 duties "
                 "on 14 partners after probing 16; Mexico and Norway "
                 "are spared."),
    },
]

# Each brief is kicker + one sentence, trimmed to wrap to at most 2 lines
# at 11pt in a 304px column (enforced by the layout assert below).
# Items 1-26 are the r6 set, re-verified this round and tightened;
# items 27-36 are the r7 density additions, each web-verified.
BRIEFS = [
    ("SHATI", "Israeli strike on a camp flat kills a family of four; 12 hurt."),
    ("GAZA TOLL", "Gaza's toll reaches 74,746; 1,679 killed since the ceasefire."),
    ("GDP", "US economy grew 4.3% in Q3, fastest in three years, BEA says."),
    ("HORMUZ", "Two oil tankers catch fire at dawn after hitting mines, IRGC says."),
    ("RAS TANURA", "Saudi defences destroy four drones over the refinery, coalition says."),
    ("MARKETS", "Asian stocks tumble as US tariff threats hit sentiment and tech fizzles."),
    ("WASHINGTON", "Trump shelves Russia business deals to end the war, FT reports."),
    ("KYIV", "Zelenskyy says a voluntary withdrawal from Donbas would be defeat."),
    ("KYIV OBLAST", "Russian attack kills one and damages shops in Bila Tserkva."),
    ("LOSSES", "Russia loses 2,091 soldiers and 15 artillery systems in a day, Kyiv says."),
    ("SAHEL", "African insurgents take the war to the skies with cheap drones, Reuters finds."),
    ("SYDNEY", "Australian core inflation runs hot at 3.8% (headline 4.9%), ABS says."),
    ("KYIV MALL", "Russian missiles hit a shopping centre late Wednesday; four hurt."),
    ("BEIJING", "China's Politburo shrinks as the graft crackdown spreads to a fourth member."),
    ("LONDON", "UK secretly sent a sex-offender refugee to Eswatini, BBC finds."),
    ("LOS ANGELES", "Thomas Markle indicted over child sex abuse images."),
    ("TAIPEI", "A China-linked network uses AI fakes to smear Taiwan candidates, BBC finds."),
    ("VETERANS", "Nuclear test veterans promised the 'full truth' as Britain orders a panel."),
    ("SPACE", "Hera unveils first images of Dimorphos; DART left a stadium-size crater."),
    ("RIYADH", "Saudi defences intercepted 209 Houthi aerial threats since September 24."),
    ("HUAWEI", "Huawei calls its US conviction 'without legal or factual merit'."),
    ("PCE", "US core inflation runs hot at 3.3%, above forecasts, before Thanksgiving."),
    ("CRYPTO", "Bitcoin falls 1% to $59,257 while ether slides 1.1% to $1,660."),
    ("OIL", "Brent crude opens 0.5% lower at $90.97 after a choppy session on Tuesday."),
    ("SEOUL", "Korean shares plunge 6.2% and Taiwan 4.8% as chip markets bear the brunt."),
    ("TOKYO", "Japan's Nikkei falls 2.8% while S&P 500 futures edge lower."),
    ("UCL", "Liverpool win 3-0 at Brugge and Barça 4-1; PSG held 2-2 by Roma."),
    ("TURKEYS", "Trump pardons Freedom and Feathers; one bolts for the bushes."),
    ("CAS", "Senegal regain the AFCON title as court overturns Morocco's 3-0 award."),
    ("CARTAGENA", "All 20 hostages freed as forces storm a supermarket; one captor killed."),
    ("QUITO", "US pauses joint military operations with Ecuador over a lethal raid probe."),
    ("MOSCOW", "Putin vows inevitable retaliation for Ukrainian strikes on refineries."),
    ("MYANMAR", "Landmine casualties hit a five-year high; Myanmar worst with 1,891."),
    ("CONGO", "WHO keeps Ebola a global emergency as cases near 11,000 in the east."),
    ("SERANG", "Candy factory fire toll reaches 26; eight workers still missing."),
    ("SANDRINGHAM", "Two charged over the Anmer Hall break-in; clock and cufflinks taken."),
]

# Ticker: two rows of four short items at 11pt bold (asserted to one line).
TICKER = [
    "Hongbo's third Tiangong trip",
    "Solomons: A$740m, 10 years",
    "Coalition hits Saada, Amran",
    "Hera: 6 months at Dimorphos",
    "Copper, tin prices fall",
    "Shenzhou-24: 90 experiments",
    "Eisenkot's first pact",
    "Sarkozy trial set for 2027",
]

STORY_COUNT = 1 + len(MEDIUM) + len(SMALL) + len(BRIEFS) + len(TICKER)


def story_count():
    """Programmatic story count: hero + medium + small + briefs + ticker."""
    return STORY_COUNT

# ---------------------------------------------------------------- helpers
def wrap_text(text, fnt, max_px, drawer):
    """Greedy word wrap; returns lines that each fit inside max_px."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if drawer.textlength(trial, font=fnt) <= max_px:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paint_lines(drawer, x, y, lines, fnt, color=INK, step=None):
    """Draw lines top-down; returns the y just below the last line."""
    if step is None:
        step = fnt.size + 3
    for line in lines:
        drawer.text((x, y), line, font=fnt, fill=color)
        y += step
    return y


def rule(drawer, x0, x1, y, color=INK, weight=1):
    drawer.line([(x0, y), (x1, y)], fill=color, width=weight)


def paint_globe(drawer, cx, cy, radius):
    """Small wireframe globe for the masthead corner."""
    drawer.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                   outline=BLUE, width=2)
    drawer.ellipse([cx - radius // 2, cy - radius,
                    cx + radius // 2, cy + radius], outline=BLUE, width=1)
    drawer.line([(cx - radius, cy), (cx + radius, cy)], fill=BLUE, width=1)
    top = cy - radius // 2
    bottom = cy + radius // 2
    drawer.arc([cx - radius, top, cx + radius, bottom], 200, 340,
               fill=BLUE, width=1)
    drawer.arc([cx - radius, top, cx + radius, bottom], 20, 160,
               fill=BLUE, width=1)


def paint_rocket(drawer, x, y, scale):
    """Simple rocket climbing past stars, drawn in the hero box.

    Coordinates below are in a 170x160 design space scaled by `scale`;
    the flame bottoms out well above the hero caption line.
    """
    def px(dx):
        return x + round(dx * scale)

    def py(dy):
        return y + round(dy * scale)

    star = SANS_B(max(10, round(16 * scale)))
    for sx, sy in [(8, 6), (150, 18), (120, 90), (20, 110), (165, 120)]:
        drawer.text((px(sx), py(sy)), "*", font=star, fill=GOLD)
    # flame: outer orange, inner yellow
    drawer.polygon([(px(62), py(118)), (px(78), py(118)), (px(70), py(150))],
                   fill=(230, 120, 40))
    drawer.polygon([(px(66), py(118)), (px(74), py(118)), (px(70), py(136))],
                   fill=(250, 200, 60))
    # fins, left then right
    drawer.polygon([(px(52), py(96)), (px(62), py(82)), (px(62), py(116))],
                   fill=RED)
    drawer.polygon([(px(88), py(96)), (px(78), py(82)), (px(78), py(116))],
                   fill=RED)
    # body with rounded top handled by the nose triangle below
    drawer.rounded_rectangle([px(58), py(20), px(82), py(120)],
                            radius=max(4, round(10 * scale)),
                            fill=(240, 240, 235), outline=BLUE, width=2)
    # nose cone
    drawer.polygon([(px(58), py(22)), (px(82), py(22)), (px(70), py(2))],
                   fill=RED)
    # porthole
    drawer.ellipse([px(63), py(46), px(77), py(60)], fill=BLUE,
                   outline=INK, width=1)
    # livery stripes
    drawer.rectangle([px(58), py(78), px(82), py(84)], fill=RED)
    drawer.rectangle([px(58), py(92), px(82), py(98)], fill=BLUE)

# ---------------------------------------------------------------- layout
def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN
    y = 14

    # ---- masthead
    d.text((x0, y), "THE WORLD IN ONE PAGE", font=SERIF_B(40), fill=INK)
    paint_globe(d, x1 - 42, y + 30, 34)
    y += 52
    d.text((x0, y), "WEDNESDAY 25 NOVEMBER 2026  •  50 VERIFIED STORIES",
           font=SANS_B(17), fill=RED)
    y += 26
    rule(d, x0, x1, y, weight=3)
    y += 6
    rule(d, x0, x1, y, weight=1)
    y += 8  # y = 110

    # ---- hero (full width)
    hy, hh = y, 172
    d.rectangle([x0, hy, x1, hy + hh], outline=INK, width=2)
    d.text((x0 + 14, hy + 10), HERO["kicker"], font=SANS_B(13), fill=RED)
    head_lines = wrap_text(HERO["headline"], SERIF_B(26), 640, d)
    assert len(head_lines) <= 2, head_lines
    hyy = paint_lines(d, x0 + 14, hy + 32, head_lines, SERIF_B(26), step=30)
    body_lines = wrap_text(HERO["body"], SANS(15), 640, d)
    assert len(body_lines) <= 4, body_lines
    paint_lines(d, x0 + 14, hyy + 6, body_lines, SANS(15), step=19)
    paint_rocket(d, x1 - 200, hy + 14, 0.8)
    d.text((x1 - 208, hy + hh - 24), "SHENZHOU-24  •  JIUQUAN",
           font=SANS_B(11), fill=GREY)
    y = hy + hh + 8  # 290

    # ---- medium row: two boxes
    my, mh = y, 146
    mw = (CW - 20) // 2
    for i, story in enumerate(MEDIUM):
        bx = x0 + i * (mw + 20)
        d.rectangle([bx, my, bx + mw, my + mh], outline=INK, width=2)
        d.text((bx + 12, my + 8), story["kicker"], font=SANS_B(12),
               fill=RED)
        hl = wrap_text(story["headline"], SANS_B(19), mw - 24, d)
        assert len(hl) <= 2, hl
        yy = paint_lines(d, bx + 12, my + 28, hl, SANS_B(19), step=22)
        bl = wrap_text(story["body"], SANS(13), mw - 24, d)
        assert len(bl) <= 4, bl
        paint_lines(d, bx + 12, yy + 4, bl, SANS(13), step=17)
    y = my + mh + 8  # 444

    # ---- small row: three boxes
    sy, sh = y, 136
    sw = (CW - 2 * 16) // 3
    for i, story in enumerate(SMALL):
        bx = x0 + i * (sw + 16)
        d.rectangle([bx, sy, bx + sw, sy + sh], outline=INK, width=1)
        d.text((bx + 10, sy + 7), story["kicker"], font=SANS_B(11),
               fill=RED)
        hl = wrap_text(story["headline"], SANS_B(16), sw - 20, d)
        assert len(hl) <= 3, hl
        yy = paint_lines(d, bx + 10, sy + 25, hl, SANS_B(16), step=19)
        bl = wrap_text(story["body"], SANS(12), sw - 20, d)
        assert len(bl) <= 3, bl
        bottom = paint_lines(d, bx + 10, yy + 3, bl, SANS(12), step=15)
        assert bottom <= sy + sh - 4, (story["kicker"], bottom, sy + sh)
    y = sy + sh + 8  # 580

    # ---- IN BRIEF header
    d.text((x0, y), "IN BRIEF", font=SANS_B(15), fill=RED)
    d.text((x1 - 190, y), "36 MORE STORIES", font=SANS_B(13), fill=GREY)
    y += 22
    rule(d, x0, x1, y, weight=1)
    y += 4  # 606

    # ---- briefs: three columns x 12, fixed 28px rows, 11pt text
    col_w = (CW - 2 * 16) // 3  # 312
    row_h = 28
    for idx, (kicker, text) in enumerate(BRIEFS):
        col = idx // 12
        row = idx % 12
        bx = x0 + col * (col_w + 16)
        by = y + row * row_h
        full = kicker + " — " + text
        lines = wrap_text(full, SANS(11), col_w - 8, d)
        assert len(lines) <= 2, (idx, lines)
        # kicker in red on the first line: redraw first line in two parts
        first = lines[0]
        klen = len(kicker) + 3  # kicker + " — "
        if len(first) >= klen and first[:len(kicker)] == kicker:
            d.text((bx, by), first[:klen], font=SANS_B(11), fill=RED)
            rest_w = d.textlength(first[:klen], font=SANS_B(11))
            d.text((bx + rest_w, by), first[klen:], font=SANS(11),
                   fill=INK)
        else:
            d.text((bx, by), first, font=SANS(11), fill=INK)
        if len(lines) > 1:
            # 12px intra-brief leading vs 28px rows: the second line
            # groups visibly with its own kicker, not the next brief.
            d.text((bx, by + 12), lines[1], font=SANS(11), fill=INK)
    y = y + 12 * row_h + 6  # 948

    # ---- ticker strip: two lines of four items
    ty, th = y, 52
    d.rectangle([x0, ty, x1, ty + th], fill=TICKER_BG)
    for row in range(2):
        items = TICKER[row * 4:(row + 1) * 4]
        line = "   •   ".join(items)
        lines = wrap_text(line, SANS_B(11), CW - 24, d)
        assert len(lines) == 1, lines
        d.text((x0 + 12, ty + 9 + row * 22), lines[0],
               font=SANS_B(11), fill=TICKER_FG)
    y = ty + th  # 1000

    assert y <= 1016, y
    img.save(path, format="PNG", optimize=True)
    return y


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    end_y = render(out)
    data = open(out, "rb").read()
    print("wrote %s (%d bytes) layout ends y=%d stories=%d sha256=%s"
          % (out, len(data), end_y, story_count(),
             hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
