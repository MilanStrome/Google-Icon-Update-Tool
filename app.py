import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
from io import BytesIO
import numpy as np

# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(page_title="Google Play Icon Radius Checker", layout="wide")

# ------------------------------------------------------------
# Premium UI CSS
# ------------------------------------------------------------
st.markdown("""
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
    div.stButton > button {
        background-color: #2563eb !important;  /* Blue */
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
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown('<div class="premium-title">Google Play Icon Radius Checker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="premium-subtitle">'
    'Google Play is updating app icon corner radius from 20% to 30%. '
    'Check if text or logos will be clipped by the new mask.'
    '</div>',
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# Your predefined apps list by categories
# Replace these URLs with your actual apps
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
# Helpers
# ------------------------------------------------------------

def clean_app_title(title: str) -> str:
    """
    Remove extra Play Store suffix from title.
    Examples:
    - "WhatsApp Messenger - Apps on Google Play" -> "WhatsApp Messenger"
    """
    if not title:
        return title

    remove_phrases = [
        " - Apps on Google Play",
        " – Apps on Google Play",
        " - Apps on Google Play™",
        " – Apps on Google Play™"
    ]

    cleaned = title
    for p in remove_phrases:
        cleaned = cleaned.replace(p, "")

    return cleaned.strip()


@st.cache_data(ttl=3600)
def fetch_play_store_data(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IconRadiusChecker/1.0)"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    title_tag = soup.find("meta", property="og:title")
    image_tag = soup.find("meta", property="og:image")

    if not title_tag or not image_tag:
        return None, None

    return title_tag.get("content"), image_tag.get("content")


@st.cache_data(ttl=3600)
def download_image(image_url: str):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IconRadiusChecker/1.0)"}
    r = requests.get(image_url, headers=headers, timeout=10)
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

    red = np.array([255, 64, 64, 150])  # RGBA
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


def parse_urls_from_text(text: str):
    urls = []
    for line in text.splitlines():
        u = line.strip()
        if not u:
            continue
        if "play.google.com/store/apps/details" in u:
            urls.append(u)
    return urls


# ------------------------------------------------------------
# Selection mode (4 selections)
# ------------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

st.write("Select category:")

# Initialize state
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
        placeholder="https://play.google.com/store/apps/details?id=com.whatsapp\nhttps://play.google.com/store/apps/details?id=com.facebook.katana",
        height=160
    )
    selected_urls = parse_urls_from_text(urls_text)
    st.caption("Only Play Store links will be used (one URL per line recommended).")

st.markdown("</div>", unsafe_allow_html=True)
# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

colA, colB, colC = st.columns([1, 1, 1])

with colA:
    preview_size = st.selectbox("Preview icon size", [256, 320, 384, 512], index=0)
with colB:
    grid_columns = st.selectbox("Results per row", [1, 2, 3], index=1)
with colC:
    show_cut_overlay = st.checkbox("Show cut zone overlay", value=True)

analyze = st.button("Analyze Icon", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Results
# ------------------------------------------------------------
if analyze:
    if not selected_urls:
        st.error("Please select at least one app or paste valid Play Store URLs.")
        st.stop()

    with st.spinner(f"Analyzing {len(selected_urls)} app(s)..."):
        results = []

        for url in selected_urls:
            try:
                app_name, icon_url = fetch_play_store_data(url)

                if not app_name or not icon_url:
                    results.append({
                        "url": url,
                        "error": "Could not detect app name or icon. Google Play might have blocked the request."
                    })
                    continue

                app_name = clean_app_title(app_name)

                icon = download_image(icon_url)
                icon_resized = icon.resize((preview_size, preview_size), Image.LANCZOS)

                mask_20 = rounded_rect_mask(preview_size, 0.20)
                mask_30 = rounded_rect_mask(preview_size, 0.30)

                icon_20 = apply_mask(icon_resized, mask_20)
                icon_30 = apply_mask(icon_resized, mask_30)

                overlay_img, cut_zone_bool = generate_cut_zone_overlay(icon_resized, mask_20, mask_30)
                risk_label, risk_score = estimate_risk(icon_resized, cut_zone_bool)

                results.append({
                    "url": url,
                    "app_name": app_name,
                    "icon_url": icon_url,
                    "icon_20": icon_20,
                    "icon_30": icon_30,
                    "overlay": overlay_img,
                    "risk_label": risk_label,
                    "risk_score": risk_score
                })

            except Exception as e:
                results.append({"url": url, "error": str(e)})

    st.subheader("Results")
    st.caption("Click app name to open the Play Store listing.")

    # Grid display
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

                # App name as hyperlink
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

                # URL clickable
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

                # st.caption(f"Risk score: {r['risk_score']:.2f}")

                # st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.write("")
st.markdown(
    "<div class='small-note'>"
    "'Built like a weapon, used like a tool.' - by MB"
    "</div>",
    unsafe_allow_html=True
)

