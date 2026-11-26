"""Draw the 25 November 2026 one-page newspaper for make.fun.

Renders a 1024x1024 broadsheet front page with 38 verified stories:
1 hero + 2 medium + 3 small + 26 IN BRIEF + 6 ticker items.
Deterministic: no network, no clock, no randomness -- every run writes
the same bytes. Run: python3 draw.py  (writes entry.png next to draw.py)
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
LINE = (26, 26, 26)
TICKER_BG = (26, 26, 26)
TICKER_FG = (253, 246, 233)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

# ---------------------------------------------------------------- stories
# Every item below was verified against a real dated source for 25 Nov 2026
# (Reuters / AP / BBC / Al Jazeera / Dawn / Xinhua / FT / Censor.net /
# Kyiv Independent / Ukrinform / CNA). Items first reported on 24 Nov
# (Champions League, Sarkozy trial, Eisenkot pact, turkey pardon,
# Senegal CAS ruling, Colombia hostages, Ecuador pause) were excluded.

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

# Each brief: kicker + one sentence, kept short enough to wrap to 2 lines
# at 12pt in a 462px column (verified by the layout assert below).
BRIEFS = [
    ("SHATI, GAZA", "Israeli strike on a Shati camp flat kills a family of four; 12 more hurt, civil defence says."),
    ("GAZA TOLL", "Gaza's death toll reaches 74,746; 1,679 have been killed since the October 2025 ceasefire."),
    ("LEBANON", "Israeli shelling hits al-Mansouri and Majdal Zoun in southern Lebanon, state news agency says."),
    ("HORMUZ", "Two oil tankers catch fire at dawn in the Strait of Hormuz after hitting mines, Iran's IRGC says."),
    ("RAS TANURA", "Saudi defences destroy four drones over the Ras Tanura oil refinery, the coalition says."),
    ("MARKETS", "Asian stocks tumble as fresh US tariff threats hit sentiment and a tech rally fizzles."),
    ("WASHINGTON", "Trump team shelves plans to use business deals with Russia to end the Ukraine war, FT reports."),
    ("KYIV", "Zelenskyy says a voluntary withdrawal from Donbas would be defeat in the war."),
    ("KYIV OBLAST", "Russian attack kills one and damages commercial infrastructure in Kyiv Oblast."),
    ("LOSSES", "Russia loses 2,091 soldiers and 15 artillery systems in a day, Kyiv's General Staff says."),
    ("SAHEL", "African insurgents take the war to the skies with cheap off-the-shelf drones, Reuters finds."),
    ("SYDNEY", "Australian inflation runs hot at 3.8%, piling pressure on the Reserve Bank to raise rates."),
    ("KYIV", "Russian ballistic missiles hit a Kyiv shopping centre late Wednesday; four hurt, two seriously."),
    ("BEIJING", "China's Politburo shrinks as the graft crackdown spreads to a fourth member since 2025."),
    ("LONDON", "UK sent a sex-offender refugee to an African country in an undisclosed resettlement deal."),
    ("LOS ANGELES", "Thomas Markle indicted in the US for possessing child sex abuse images."),
    ("TAIPEI", "A China-linked network uses AI fakes to smear Taiwan election candidates, BBC Verify finds."),
    ("LONDON", "Nuclear test veterans will get the 'full truth' as Britain orders an independent panel."),
    ("SPACE", "ESA's Hera unveils first close-up images of Dimorphos; DART left a stadium-size crater."),
    ("RIYADH", "Saudi defences have intercepted 209 Houthi aerial threats since September 24, embassy says."),
    ("HUAWEI", "Huawei calls its US conviction 'without legal or factual merit' and vows legal action."),
    ("WASHINGTON", "US core PCE inflation runs hot at 3.3%, above forecasts, ahead of the Thanksgiving holiday."),
    ("CRYPTO", "Bitcoin falls 1% to $59,257 while ether slides 1.1% to $1,660."),
    ("OIL", "Brent crude opens 0.5% lower at $90.97 after a choppy session on Tuesday."),
    ("SEOUL", "Korean shares plunge 6.2% and Taiwan 4.8% as chip markets bear the brunt."),
    ("TOKYO", "Japan's Nikkei falls 2.8% while S&P 500 futures edge lower."),
]

TICKER = [
    "Tang Hongbo's third trip to Tiangong",
    "Solomons: A$740m over a decade",
    "Coalition hits Saada and Amran",
    "Hera: six months studying Dimorphos",
    "Copper, tin prices fall sharply",
    "Shenzhou-24: 90 experiments planned",
]

STORY_COUNT = 1 + len(MEDIUM) + len(SMALL) + len(BRIEFS) + len(TICKER)


def story_count():
    """Programmatic story count: hero + medium + small + briefs + ticker."""
    return STORY_COUNT


# ---------------------------------------------------------------- helpers
def wrap(text, fnt, width, draw):
    """Greedy word wrap; returns a list of lines that fit in `width` px."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill=INK, leading=None):
    """Draw lines top-down; returns the y just below the last line."""
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_globe(draw, cx, cy, r):
    """Small wireframe globe for the masthead corner."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=2)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=BLUE, width=1)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=BLUE, width=1)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 200, 340, fill=BLUE, width=1)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 20, 160, fill=BLUE, width=1)


def draw_rocket(draw, x, y, s):
    """Simple rocket climbing past stars, drawn in the hero box.

    All offsets are scaled by `s` so the flame never reaches the
    caption line at the bottom of the hero box.
    """
    def px(dx):
        return x + round(dx * s)

    def py(dy):
        return y + round(dy * s)

    for sx, sy in [(8, 6), (150, 18), (120, 90), (20, 110), (165, 120)]:
        draw.text((px(sx), py(sy)), "*", font=SANS_B(max(10, round(16 * s))),
                  fill=GOLD)
    # flame
    draw.polygon([(px(62), py(118)), (px(78), py(118)), (px(70), py(150))],
                 fill=(230, 120, 40))
    draw.polygon([(px(66), py(118)), (px(74), py(118)), (px(70), py(136))],
                 fill=(250, 200, 60))
    # fins
    draw.polygon([(px(52), py(96)), (px(62), py(82)), (px(62), py(116))],
                 fill=RED)
    draw.polygon([(px(88), py(96)), (px(78), py(82)), (px(78), py(116))],
                 fill=RED)
    # body
    draw.rounded_rectangle([px(58), py(20), px(82), py(120)],
                           radius=max(4, round(10 * s)),
                           fill=(240, 240, 235), outline=BLUE, width=2)
    # nose
    draw.polygon([(px(58), py(22)), (px(82), py(22)), (px(70), py(2))],
                 fill=RED)
    # window
    draw.ellipse([px(63), py(46), px(77), py(60)], fill=BLUE,
                 outline=INK, width=1)
    # stripes
    draw.rectangle([px(58), py(78), px(82), py(84)], fill=RED)
    draw.rectangle([px(58), py(92), px(82), py(98)], fill=BLUE)


# ---------------------------------------------------------------- layout
def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN
    y = 14

    # ---- masthead
    d.text((x0, y), "THE WORLD IN ONE PAGE", font=SERIF_B(40), fill=INK)
    draw_globe(d, x1 - 42, y + 30, 34)
    y += 52
    d.text((x0, y), "WEDNESDAY 25 NOVEMBER 2026  •  38 VERIFIED STORIES",
           font=SANS_B(17), fill=RED)
    y += 26
    hline(d, x0, x1, y, width=3)
    y += 6
    hline(d, x0, x1, y, width=1)
    y += 8  # y = 110

    # ---- hero (full width)
    hy, hh = y, 172
    d.rectangle([x0, hy, x1, hy + hh], outline=INK, width=2)
    d.text((x0 + 14, hy + 10), HERO["kicker"], font=SANS_B(13), fill=RED)
    head_lines = wrap(HERO["headline"], SERIF_B(26), 640, d)
    assert len(head_lines) <= 2, head_lines
    hyy = draw_lines(d, x0 + 14, hy + 32, head_lines, SERIF_B(26),
                     leading=30)
    body_lines = wrap(HERO["body"], SANS(15), 640, d)
    assert len(body_lines) <= 4, body_lines
    draw_lines(d, x0 + 14, hyy + 6, body_lines, SANS(15), leading=19)
    draw_rocket(d, x1 - 200, hy + 14, 0.8)
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
        hl = wrap(story["headline"], SANS_B(19), mw - 24, d)
        assert len(hl) <= 2, hl
        yy = draw_lines(d, bx + 12, my + 28, hl, SANS_B(19), leading=22)
        bl = wrap(story["body"], SANS(13), mw - 24, d)
        assert len(bl) <= 4, bl
        draw_lines(d, bx + 12, yy + 4, bl, SANS(13), leading=17)
    y = my + mh + 8  # 444

    # ---- small row: three boxes
    sy, sh = y, 136
    sw = (CW - 2 * 16) // 3
    for i, story in enumerate(SMALL):
        bx = x0 + i * (sw + 16)
        d.rectangle([bx, sy, bx + sw, sy + sh], outline=INK, width=1)
        d.text((bx + 10, sy + 7), story["kicker"], font=SANS_B(11),
               fill=RED)
        hl = wrap(story["headline"], SANS_B(16), sw - 20, d)
        assert len(hl) <= 3, hl
        yy = draw_lines(d, bx + 10, sy + 25, hl, SANS_B(16), leading=19)
        bl = wrap(story["body"], SANS(12), sw - 20, d)
        assert len(bl) <= 3, bl
        bottom = draw_lines(d, bx + 10, yy + 3, bl, SANS(12), leading=15)
        assert bottom <= sy + sh - 4, (story["kicker"], bottom, sy + sh)
    y = sy + sh + 8  # 580

    # ---- IN BRIEF header
    d.text((x0, y), "IN BRIEF", font=SANS_B(15), fill=RED)
    d.text((x1 - 190, y), "26 MORE STORIES", font=SANS_B(13), fill=GREY)
    y += 22
    hline(d, x0, x1, y, width=1)
    y += 4  # 606

    # ---- briefs: two columns x 13, fixed 26px rows
    col_w = (CW - 20) // 2
    row_h = 26
    for idx, (kicker, text) in enumerate(BRIEFS):
        col = idx // 13
        row = idx % 13
        bx = x0 + col * (col_w + 20)
        by = y + row * row_h
        full = kicker + " — " + text
        lines = wrap(full, SANS(12), col_w - 8, d)
        assert len(lines) <= 2, (idx, lines)
        # kicker in red on the first line: redraw first line in two parts
        first = lines[0]
        klen = len(kicker) + 3  # kicker + " — "
        if len(first) >= klen and first[:len(kicker)] == kicker:
            d.text((bx, by), first[:klen], font=SANS_B(12), fill=RED)
            rest_w = d.textlength(first[:klen], font=SANS_B(12))
            d.text((bx + rest_w, by), first[klen:], font=SANS(12),
                   fill=INK)
        else:
            d.text((bx, by), first, font=SANS(12), fill=INK)
        if len(lines) > 1:
            d.text((bx, by + 13), lines[1], font=SANS(12), fill=INK)
    y = y + 13 * row_h + 6  # 950

    # ---- ticker strip: two lines of three items
    ty, th = y, 52
    d.rectangle([x0, ty, x1, ty + th], fill=TICKER_BG)
    for row in range(2):
        items = TICKER[row * 3:(row + 1) * 3]
        line = "   •   ".join(items)
        lines = wrap(line, SANS_B(12), CW - 24, d)
        assert len(lines) == 1, lines
        d.text((x0 + 12, ty + 7 + row * 24), lines[0],
               font=SANS_B(12), fill=TICKER_FG)
    y = ty + th  # 1010

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
