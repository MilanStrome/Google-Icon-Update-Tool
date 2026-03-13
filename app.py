import hashlib
from io import BytesIO
from urllib.parse import parse_qs, urlencode, urlparse

import numpy as np
import requests
import streamlit as st
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw

# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(page_title="Google Play Icon Radius Checker", layout="wide")

# ------------------------------------------------------------
# Premium UI CSS
# ------------------------------------------------------------
st.markdown(
    """
<style>
    .main {
        padding-top: 1.0rem;
    }
    .premium-title {
        font-size: 34px;
        font-weight: 900;
        letter-spacing: -0.6px;
        margin-bottom: 0.25rem;
    }
    .premium-subtitle {
        font-size: 15px;
        color: #6b7280;
        margin-bottom: 1.25rem;
        line-height: 1.5;
    }
    .card {
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 16px;
        padding: 16px;
        background: white;
        box-shadow: 0px 10px 22px rgba(0,0,0,0.05);
        margin-bottom: 14px;
    }
    .label {
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 0.4rem;
        line-height: 1.25;
    }
    .mini-caption {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 12px;
        word-break: break-all;
    }
    .badge-safe {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        margin-left: 10px;
        vertical-align: middle;
    }
    .badge-warn {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        background: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
        margin-left: 10px;
        vertical-align: middle;
    }
    .badge-high {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        background: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fecaca;
        margin-left: 10px;
        vertical-align: middle;
    }
    .small-note {
        font-size: 15px;
        font-weight: 800;
        color: #00008B;
    }
    .locale-chip {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .section-subtitle {
        font-size: 13px;
        font-weight: 700;
        color: #374151;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    div.stButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: 1px solid #1d4ed8 !important;
        padding: 0.7rem 1.2rem !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        transition: 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        border-color: #1e40af !important;
        color: white !important;
        transform: translateY(-1px);
    }
    div.stButton > button:active {
        transform: translateY(0px);
        background-color: #1e40af !important;
        border-color: #1e3a8a !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown(
    '<div class="premium-title">Google Play Icon Radius Checker</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="premium-subtitle">'
    "Google Play is updating app icon corner radius from 20% to 30%. "
    "Check if text or logos will be clipped by the new mask. "
    "Also scan Google Play localized listings and detect where the icon is different from the default US icon."
    "</div>",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Your predefined apps list by categories
# ------------------------------------------------------------
APP_CATEGORIES = {
    "Kids Games": [
        {
            "name": "ABC Kids: Tracing & Phonics",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.abc_kids_toddler_tracing_phonics"
        },
        {
            "name": "Spelling & Phonics: Kids Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.abc.spelling.toddler.spell.phonics"
        },
        {
            "name": "123 Numbers - Count & Tracing",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.numbers123.toddler.counting.tracing"
        },
        {
            "name": "Puzzle Kids: Jigsaw Puzzles",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.jigsaw.puzzles.kids"
        },
        {
            "name": "Math Kids: Math Games For Kids",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.math.kids.counting"
        },
        {
            "name": "Color Kids: Coloring Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.shapes.colors.toddler"
        },
        {
            "name": "Kids Multiplication Math Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.kids.multiplication.games.multiply.math"
        },
        {
            "name": "Baby Games: Piano & Baby Phone",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.baby.games.piano.phone.kids"
        },
        {
            "name": "Coloring Games: Color & Paint",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.kids.coloring.book.color.painting"
        },
        {
            "name": "Learn to Read: Kids Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.sight.words.phonics.reading.kids.games"
        },
        {
            "name": "Math Games: Math for Kids",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.math.games.kids.addition.subtraction.multiplication.division"
        },
        {
            "name": "Kids Math: Math Games for Kids",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.montessori.math.games.kids.number.counting"
        },
        {
            "name": "Drawing Games: Draw & Color",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.kids.drawing.games.coloring.book.paint"
        },
        {
            "name": "Kids Games: For Toddlers 3-5",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.baby.toddler.kids.games.learning.activity"
        },
        {
            "name": "Kids Toddler & Preschool Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.toddler.preschool.kids.learning.games"
        },
        {
            "name": "Baby Phone & Kids Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.baby.phone.kids.games.toddler.learning.apps.lucas.and.friends"
        },
        {
            "name": "Kids Music: Piano, Xylo, Drums",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.kids.games.music.baby.piano.songs.lucas.and.friends"
        }
    ],
    "General Games": [
        {
            "name": "Balloon Pop: Match 3 Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.match3_balloon_puzzle_game"
        },
        {
            "name": "Basketball Games: Hoop Puzzles",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.basketball"
        },
        {
            "name": "Block Puzzle: Block Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.block.jigsaw.puzzle.game.hexa.color"
        },
        {
            "name": "Block Puzzles: Hexa Block Game",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.block.puzzle.games.classic.board"
        },
        {
            "name": "Bloody Monsters: Bouncy Bullet",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.bloodymonsters"
        },
        {
            "name": "Bubble Crusher: Bubble Pop",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.bubblecrusher2"
        },
        {
            "name": "Bubble Pop: Bubble Shooter",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.bubble.shooter.shoot.bubbles"
        },
        {
            "name": "Bubble Shooter: Pastry Pop",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.bubble.pop.bubble.shooter.puzzle.game.match3"
        },
        {
            "name": "Cake Blast: Match 3 Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.cake.match3.puzzle.game"
        },
        {
            "name": "Christmas Cookie: Match 3 Game",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.christmascookie"
        },
        {
            "name": "Dice Puzzle - Dice Merge Game",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.dice.games.merge.puzzle"
        },
        {
            "name": "Find The Difference: Find It",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.find.odd.one.out.spot.puzzle.game"
        },
        {
            "name": "Find The Differences - Spot it",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.puzzle.game.find.difference.ftd"
        },
        {
            "name": "Finger Slayer",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.fingerslayer"
        },
        {
            "name": "Fruit Cube Blast",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.tap.blast.match3.puzzle"
        },
        {
            "name": "Gummy Paradise: Match 3 Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.gummy.paradise.drag.match"
        },
        {
            "name": "Ice Cream Paradise: Match 3",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.ice.cream.paradise.match3"
        },
        {
            "name": "Jewel Gems: Jewel Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.jewel.gem.tap.cube.blast.puzzle.match3.game"
        },
        {
            "name": "Jigsaw Puzzles Blocks",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.tangram.jigsaw.puzzles.block.game"
        },
        {
            "name": "Jigsaw Puzzles Hexa",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.hexa.jigsaw.puzzle.block.game"
        },
        {
            "name": "Jigsaw Puzzles: Picture Puzzle",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.jigsaw.puzzles"
        },
        {
            "name": "Match Tiles: Block Puzzle Game",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.tile.match3.block.puzzle.game"
        },
        {
            "name": "Maze Games: Labyrinth Puzzles",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.maze.games.puzzle.mazes.labyrinth"
        },
        {
            "name": "Onnet Connect: Tile Matching",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.tile.connect.link.puzzle.game"
        },
        {
            "name": "Puzzles: Jigsaw Puzzle Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.jigsaw.puzzles.picture.block.games"
        },
        {
            "name": "Tangram Puzzle: Polygrams Game",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.tangram.blocks.puzzle.brain.games"
        },
        {
            "name": "Tile Puzzle Game: Tiles Match",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.tile.match.tiles.puzzle.game"
        },
        {
            "name": "Veggies Cut: Logic Puzzle Game",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.veggies.cut.logic.puzzle.adult.game"
        },
        {
            "name": "Word Pics - Word Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.two.pics.one.word.puzzle.game"
        },
        {
            "name": "Word Puzzle: Word Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.four.pics.one.word.pic.to.words.puzzle.game"
        },
        {
            "name": "Word Search Games: Word Find",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.word.search.puzzle.game"
        },
        {
            "name": "Word Spin: Word Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.pic.word.games.guess.picture.puzzle"
        },
        {
            "name": "Zombie Heroes: Zombie Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.lastheroes"
        },
        {
            "name": "Zombie Ragdoll - Zombie Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.zombieragdoll"
        },
        {
            "name": "Zombie Shooting: Archery Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.archeryblitz1"
        },
        {
            "name": "Zombie Slice: Zombie Games",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.zombiecarnage"
        }
    ],
    "Applications": [
        {
            "name": "Alarm Clock: Mornings & Naps",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.alarm.clock.smart.sleep.timer.music"
        },
        {
            "name": "App Locker: Privacy Apps Lock",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.applock.protect.lock.app"
        },
        {
            "name": "Digital Compass: Map & GPS",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.compass.offline.direction"
        },
        {
            "name": "Flash Alerts LED - Call, SMS",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.Flash.Alerts.LED.Call.SMS.Flashlight"
        },
        {
            "name": "Flashlight: Torch Light",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.flashlight"
        },
        {
            "name": "Magnifying Glass + Flashlight",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.magnifyingglass"
        },
        {
            "name": "Mirror: Beauty Camera",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.mirror"
        },
        {
            "name": "QR Scanner and Generator",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.qr.barcode.scanner.reader.generator"
        },
        {
            "name": "Sleep Timer: Turn Music Off",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.sleep.timer.off.music.relax"
        },
        {
            "name": "Smart Calc: Daily Calculator",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.calculator.free.app"
        },
        {
            "name": "Stopwatch and Timer",
            "url": "https://play.google.com/store/apps/details?id=com.rvappstudios.timer.multiple.alarm.stopwatch"
        }
    ],
}

# ------------------------------------------------------------
# Google Play supported languages provided by you
# ------------------------------------------------------------
GOOGLE_PLAY_LANGUAGE_CODES = [
    ("Afrikaans", "af"),
    ("Albanian", "sq"),
    ("Amharic", "am"),
    ("Arabic", "ar"),
    ("Armenian", "hy-AM"),
    ("Azerbaijani", "az-AZ"),
    ("Bengali (Bangladesh)", "bn-BD"),
    ("Basque", "eu-ES"),
    ("Belarusian", "be"),
    ("Bulgarian", "bg"),
    ("Burmese", "my-MM"),
    ("Catalan", "ca"),
    ("Chinese (Simplified)", "zh-CN"),
    ("Chinese (Traditional)", "zh-TW"),
    ("Chinese (Hong Kong)", "zh-HK"),
    ("Croatian", "hr"),
    ("Czech", "cs-CZ"),
    ("Danish", "da-DK"),
    ("Dutch", "nl-NL"),
    ("English", "en"),
    ("English (Australia)", "en-AU"),
    ("English (Canada)", "en-CA"),
    ("English (Great Britain)", "en-GB"),
    ("English (India)", "en-IN"),
    ("English (Singapore)", "en-SG"),
    ("English (South Africa)", "en-ZA"),
    ("Estonian", "et"),
    ("Filipino", "fil"),
    ("Finnish", "fi-FI"),
    ("French (Canada)", "fr-CA"),
    ("French (France)", "fr-FR"),
    ("Galician", "gl-ES"),
    ("Georgian", "ka-GE"),
    ("German", "de-DE"),
    ("Greek", "el-GR"),
    ("Gujarati", "gu"),
    ("Hebrew", "iw-IL"),
    ("Hindi", "hi-IN"),
    ("Hungarian", "hu-HU"),
    ("Icelandic", "is-IS"),
    ("Indonesian", "id"),
    ("Italian", "it-IT"),
    ("Japanese", "ja-JP"),
    ("Kannada", "kn-IN"),
    ("Kazakh", "kk"),
    ("Khmer", "km-KH"),
    ("Korean", "ko-KR"),
    ("Kyrgyz", "ky-KG"),
    ("Lao", "lo-LA"),
    ("Latvian", "lv"),
    ("Lithuanian", "lt"),
    ("Macedonian", "mk-MK"),
    ("Malay", "ms"),
    ("Malay (Malaysia)", "ms-MY"),
    ("Malayalam", "ml-IN"),
    ("Marathi", "mr-IN"),
    ("Mongolian", "mn-MN"),
    ("Nepali", "ne-NP"),
    ("Norwegian", "no-NO"),
    ("Persian", "fa"),
    ("Persian (Afghanistan)", "fa-AF"),
    ("Persian (Iran)", "fa-IR"),
    ("Persian (United Arab Emirates)", "fa-AE"),
    ("Polish", "pl-PL"),
    ("Portuguese (Brazil)", "pt-BR"),
    ("Portuguese (Portugal)", "pt-PT"),
    ("Punjabi", "pa"),
    ("Romanian", "ro"),
    ("Romansh", "rm"),
    ("Russian", "ru"),
    ("Serbian", "sr"),
    ("Sinhala", "si-LK"),
    ("Slovak", "sk"),
    ("Slovenian", "sl"),
    ("Spanish (Latin America)", "es-419"),
    ("Spanish (Spain)", "es-ES"),
    ("Spanish (United States)", "es-US"),
    ("Swahili", "sw"),
    ("Swedish", "sv-SE"),
    ("Tamil", "ta-IN"),
    ("Telugu", "te-IN"),
    ("Thai", "th"),
    ("Turkish", "tr-TR"),
    ("Ukrainian", "uk"),
    ("Urdu", "ur"),
    ("Vietnamese", "vi"),
    ("Zulu", "zu"),
]

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def clean_app_title(title: str) -> str:
    if not title:
        return title

    remove_phrases = [
        " - Apps on Google Play",
        " – Apps on Google Play",
        " - Apps on Google Play™",
        " – Apps on Google Play™",
    ]

    cleaned = title
    for p in remove_phrases:
        cleaned = cleaned.replace(p, "")

    return cleaned.strip()


def parse_app_id(url: str) -> str:
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        return qs.get("id", [""])[0].strip()
    except Exception:
        return ""


def build_play_store_url(app_id: str, hl: str = "en-US", gl: str = "US") -> str:
    base = "https://play.google.com/store/apps/details"
    params = {
        "id": app_id,
        "hl": hl,
        "gl": gl,
    }
    return f"{base}?{urlencode(params)}"


def normalize_store_url(url: str, hl: str = "en-US", gl: str = "US") -> str:
    app_id = parse_app_id(url)
    if not app_id:
        return url
    return build_play_store_url(app_id, hl=hl, gl=gl)


def parse_urls_from_text(text: str):
    urls = []
    for line in text.splitlines():
        u = line.strip()
        if not u:
            continue
        if "play.google.com/store/apps/details" in u:
            urls.append(u)
    return urls


def parse_locale_code(code: str):
    code = code.strip()

    if "-" in code:
        parts = code.split("-")
        region = parts[-1].upper()

        if len(region) == 2 and region.isalpha():
            return code, region

        return code, ""

    return code, ""


def get_supported_locales():
    locales = []
    for language_name, code in GOOGLE_PLAY_LANGUAGE_CODES:
        hl, gl = parse_locale_code(code)
        locales.append(
            {
                "label": language_name,
                "code": code,
                "hl": hl,
                "gl": gl,
            }
        )
    return locales


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_play_store_data(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; IconRadiusChecker/2.0)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    title_tag = soup.find("meta", property="og:title")
    image_tag = soup.find("meta", property="og:image")

    if not title_tag or not image_tag:
        return None, None

    return title_tag.get("content"), image_tag.get("content")


@st.cache_data(ttl=3600, show_spinner=False)
def download_image(image_url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; IconRadiusChecker/2.0)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(image_url, headers=headers, timeout=20)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGBA")


def rounded_rect_mask(size: int, radius_percent: float):
    radius_px = int(size * radius_percent)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, size, size], radius=radius_px, fill=255)
    return mask


def apply_mask(icon: Image.Image, mask: Image.Image):
    out = icon.copy()
    out.putalpha(mask)
    return out


def generate_cut_zone_overlay(icon: Image.Image, mask_20: Image.Image, mask_30: Image.Image):
    m20 = np.array(mask_20) / 255.0
    m30 = np.array(mask_30) / 255.0
    cut_zone = (m20 > 0.5) & (m30 < 0.5)

    overlay = icon.copy()
    overlay_np = np.array(overlay)

    red = np.array([255, 64, 64, 150])
    overlay_np[cut_zone] = red

    return Image.fromarray(overlay_np, "RGBA"), cut_zone


def estimate_risk(icon: Image.Image, cut_zone_bool):
    icon_np = np.array(icon)
    cut_pixels = icon_np[cut_zone_bool]

    if cut_pixels.shape[0] < 50:
        return "Safe", 0.0

    rgb = cut_pixels[:, :3].astype(np.float32)
    mean = rgb.mean(axis=0)
    dist = np.linalg.norm(rgb - mean, axis=1)

    risk_score = float(np.mean(dist))

    if risk_score > 35:
        return "High risk of clipping", risk_score
    elif risk_score > 20:
        return "Some risk of clipping", risk_score
    else:
        return "Safe", risk_score


def image_fingerprint(image: Image.Image, size: int = 128) -> str:
    img = image.convert("RGBA").resize((size, size), Image.LANCZOS)
    return hashlib.sha256(img.tobytes()).hexdigest()


def image_diff_score(img1: Image.Image, img2: Image.Image, size: int = 128) -> float:
    a = np.asarray(img1.convert("RGBA").resize((size, size), Image.LANCZOS), dtype=np.float32)
    b = np.asarray(img2.convert("RGBA").resize((size, size), Image.LANCZOS), dtype=np.float32)
    return float(np.mean(np.abs(a - b)))


def find_localized_icon_differences(base_url: str, base_icon: Image.Image, app_name_for_status: str = ""):
    app_id = parse_app_id(base_url)
    if not app_id:
        return [], []

    locales = get_supported_locales()
    base_hash = image_fingerprint(base_icon)
    diffs = []
    scan_errors = []

    lang_progress = st.progress(0, text=f"Scanning localized icons for {app_name_for_status}...")
    lang_status = st.empty()

    total_locales = len(locales)

    for idx, locale in enumerate(locales, start=1):
        progress_value = idx / total_locales
        lang_progress.progress(
            progress_value,
            text=f"Scanning localized icons for {app_name_for_status}... ({idx}/{total_locales})"
        )
        lang_status.info(f"Checking language: {locale['label']} [{locale['code']}]")

        if locale["hl"] in ["en", "en-US"] and locale["gl"] == "US":
            continue

        try:
            gl_value = locale["gl"] if locale["gl"] else "US"
            localized_url = build_play_store_url(app_id, hl=locale["hl"], gl=gl_value)

            localized_title, localized_icon_url = fetch_play_store_data(localized_url)

            if not localized_icon_url:
                continue

            localized_icon = download_image(localized_icon_url)
            localized_hash = image_fingerprint(localized_icon)

            if localized_hash != base_hash:
                diff_score = image_diff_score(base_icon, localized_icon)

                diffs.append(
                    {
                        "label": locale["label"],
                        "code": locale["code"],
                        "hl": locale["hl"],
                        "gl": gl_value,
                        "url": localized_url,
                        "app_name": clean_app_title(localized_title or ""),
                        "icon_url": localized_icon_url,
                        "icon": localized_icon,
                        "diff_score": diff_score,
                    }
                )
        except Exception as e:
            scan_errors.append(f"{locale['label']}: {str(e)}")

    lang_progress.empty()
    lang_status.empty()

    diffs = sorted(diffs, key=lambda x: (-x["diff_score"], x["label"]))
    return diffs, scan_errors


# ------------------------------------------------------------
# Selection mode
# ------------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.write("Select category:")

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "Kids Games"


def set_category(cat):
    st.session_state.selected_category = cat


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.checkbox(
        "Kids Games",
        value=(st.session_state.selected_category == "Kids Games"),
        on_change=set_category,
        args=("Kids Games",)
    )

with col2:
    st.checkbox(
        "Applications",
        value=(st.session_state.selected_category == "Applications"),
        on_change=set_category,
        args=("Applications",)
    )

with col3:
    st.checkbox(
        "General Games",
        value=(st.session_state.selected_category == "General Games"),
        on_change=set_category,
        args=("General Games",)
    )

with col4:
    st.checkbox(
        "Paste PlayStore URL",
        value=(st.session_state.selected_category == "Paste PlayStore URL"),
        on_change=set_category,
        args=("Paste PlayStore URL",)
    )

mode = st.session_state.selected_category
selected_urls = []

if mode in ["Kids Games", "Applications", "General Games"]:
    apps_list = APP_CATEGORIES.get(mode, [])
    st.write(f"Select apps from **{mode}** list:")

    app_names = [a["name"] for a in apps_list]

    selected_apps = st.multiselect(
        "Select apps",
        options=app_names,
        default=app_names
    )

    selected_urls = [a["url"] for a in apps_list if a["name"] in selected_apps]

else:
    st.write("Paste multiple Play Store URLs (one per line).")
    urls_text = st.text_area(
        "Play Store links",
        placeholder="https://play.google.com/store/apps/details?id=com.whatsapp\nhttps://play.google.com/store/apps/details?id=com.moonactive.coinmaster",
        height=160
    )
    selected_urls = parse_urls_from_text(urls_text)
    st.caption("Only Play Store links will be used (one URL per line recommended).")

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

colA, colB, colC, colD = st.columns([1, 1, 1, 1])

with colA:
    preview_size = st.selectbox("Preview icon size", [256, 320, 384, 512], index=0)
with colB:
    grid_columns = st.selectbox("Results per row", [1, 2, 3], index=1)
with colC:
    show_cut_overlay = st.checkbox("Show cut zone overlay", value=True)
with colD:
    scan_localized_icons = st.checkbox("Scan localized Play icons", value=True)

localized_preview_size = st.selectbox(
    "Localized icon preview size",
    [96, 128, 160, 192],
    index=1
)

analyze = st.button("Analyze Icon", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Results
# ------------------------------------------------------------
if analyze:
    if not selected_urls:
        st.error("Please select at least one app or paste valid Play Store URLs.")
        st.stop()

    results = []
    total_apps = len(selected_urls)

    overall_progress = st.progress(0, text="Starting analysis...")
    overall_status = st.empty()

    for app_index, original_url in enumerate(selected_urls, start=1):
        overall_progress.progress(
            app_index / total_apps,
            text=f"Analyzing apps... ({app_index}/{total_apps})"
        )
        overall_status.info(f"Processing app {app_index} of {total_apps}")

        try:
            us_url = normalize_store_url(original_url, hl="en-US", gl="US")
            app_name, icon_url = fetch_play_store_data(us_url)

            if not app_name or not icon_url:
                results.append({
                    "url": original_url,
                    "error": "Could not detect app name or icon. Google Play might have blocked the request."
                })
                continue

            app_name = clean_app_title(app_name)
            overall_status.info(f"Processing app {app_index} of {total_apps}: {app_name}")

            icon = download_image(icon_url)
            icon_resized = icon.resize((preview_size, preview_size), Image.LANCZOS)

            mask_20 = rounded_rect_mask(preview_size, 0.20)
            mask_30 = rounded_rect_mask(preview_size, 0.30)

            icon_20 = apply_mask(icon_resized, mask_20)
            icon_30 = apply_mask(icon_resized, mask_30)

            overlay_img, cut_zone_bool = generate_cut_zone_overlay(icon_resized, mask_20, mask_30)
            risk_label, risk_score = estimate_risk(icon_resized, cut_zone_bool)

            localized_differences = []
            locale_scan_errors = []

            if scan_localized_icons:
                localized_differences, locale_scan_errors = find_localized_icon_differences(
                    us_url,
                    icon,
                    app_name_for_status=app_name
                )

            results.append({
                "url": us_url,
                "source_url": original_url,
                "app_name": app_name,
                "icon_url": icon_url,
                "icon_20": icon_20,
                "icon_30": icon_30,
                "overlay": overlay_img,
                "risk_label": risk_label,
                "risk_score": risk_score,
                "localized_differences": localized_differences,
                "locale_scan_errors": locale_scan_errors,
            })

        except Exception as e:
            results.append({"url": original_url, "error": str(e)})

    overall_progress.empty()
    overall_status.empty()

    st.subheader("Results")

    rows = [results[i:i + grid_columns] for i in range(0, len(results), grid_columns)]

    for row in rows:
        cols = st.columns(grid_columns)

        for idx, r in enumerate(row):
            with cols[idx]:
                st.markdown('<div class="card">', unsafe_allow_html=True)

                if "error" in r:
                    st.error("Failed")
                    st.markdown(f"<div class='mini-caption'>{r['url']}</div>", unsafe_allow_html=True)
                    st.write(r["error"])
                    st.markdown("</div>", unsafe_allow_html=True)
                    continue

                if "High risk" in r["risk_label"]:
                    badge = '<span class="badge-high">High risk</span>'
                elif "Some risk" in r["risk_label"]:
                    badge = '<span class="badge-warn">Some risk</span>'
                else:
                    badge = '<span class="badge-safe">Safe</span>'

                st.markdown(
                    f"""
                    <div class='label'>
                        <a href="{r['url']}" target="_blank" style="text-decoration:none; color: inherit;">
                            {r['app_name']}
                        </a>
                        {badge}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <div class='mini-caption'>
                        <a href="{r['url']}" target="_blank" style="color:#6b7280; text-decoration:none;">
                            {r['url']}
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.caption("1) 20%")
                    st.image(r["icon_20"], use_container_width=True)

                with c2:
                    st.caption("2) 30%")
                    st.image(r["icon_30"], use_container_width=True)

                with c3:
                    st.caption("3) Cut zone")
                    if show_cut_overlay:
                        st.image(r["overlay"], use_container_width=True)
                    else:
                        st.image(r["icon_30"], use_container_width=True)

                if scan_localized_icons:
                    diff_count = len(r["localized_differences"])

                    if diff_count > 0:
                        st.markdown(
                            f"<div class='section-subtitle'>Different localized icons found: {diff_count}</div>",
                            unsafe_allow_html=True
                        )

                        chips = []
                        for item in r["localized_differences"]:
                            chips.append(f"<span class='locale-chip'>{item['label']}</span>")
                        st.markdown("".join(chips), unsafe_allow_html=True)

                        with st.expander("Show different localized icons", expanded=False):
                            preview_cols = st.columns(3)

                            for i, loc in enumerate(r["localized_differences"]):
                                with preview_cols[i % 3]:
                                    localized_preview = loc["icon"].resize(
                                        (localized_preview_size, localized_preview_size),
                                        Image.LANCZOS
                                    )
                                    st.image(localized_preview, caption=loc["label"], use_container_width=False)
                                    # st.caption(f"Language code: {loc['code']}")
                                    # st.caption(f"hl={loc['hl']} | gl={loc['gl']}")
                                    # st.caption(f"Difference score: {loc['diff_score']:.2f}")
                                    st.markdown(f"[Open listing]({loc['url']})")
                    else:
                        st.markdown(
                            "<div class='section-subtitle'>Localized icon scan: no differences found from default US icon.</div>",
                            unsafe_allow_html=True
                        )

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.write("")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='small-note'>"
    "✶ Built like a weapon, use like a tool. ✶"
    "</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='small-note'>"
    "- by Ex-Code Warrior Ⓜ"
    "</div>",
    unsafe_allow_html=True
)
