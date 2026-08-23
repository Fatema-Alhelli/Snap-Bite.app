
import os
import json
import random
import base64
import io
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

# ----------------------------
# Snap-Bite configuration
# ----------------------------
st.set_page_config(
    page_title="Snap-Bite",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR / "assets"
RECIPES_FILE = BASE_DIR / "recipes.json"
MODEL_FILE = BASE_DIR / "models" / "best.pt"

GREEN_DARK = "#054023"
GREEN = "#1E6D4A"
LEAF = "#A5D08C"
YELLOW = "#F6B454"
ORANGE = "#FD893E"
CREAM = "#F9EFDE"
WHITE = "#FFFFFF"

INGREDIENT_EMOJIS = {
    "chicken": "🍗", "rice": "🍚", "onion": "🧅", "tomato": "🍅",
    "spices": "🌶️", "vermicelli": "🍜", "egg": "🥚", "sugar": "🍬",
    "cardamom": "🌿", "saffron": "🌼", "chickpeas": "🫘", "tahini": "🥣",
    "lemon": "🍋", "garlic": "🧄", "olive oil": "🫒", "yogurt": "🥛",
    "cream": "🥛", "butter": "🧈", "potato": "🥔", "peas": "🫛",
    "flour": "🌾", "noodles": "🍜", "mushroom": "🍄", "soy sauce": "🥢",
    "broccoli": "🥦", "carrot": "🥕", "pepper": "🫑", "pineapple": "🍍",
    "vinegar": "🫗", "pasta": "🍝", "milk": "🥛", "cheese": "🧀",
    "basil": "🌿", "bread": "🍞", "parsley": "🌿", "nori": "🌿",
    "cucumber": "🥒", "avocado": "🥑", "olive": "🫒", "tortilla": "🌯",
    "strawberry": "🍓", "banana": "🍌", "honey": "🍯", "cocoa": "🍫",
}

# ----------------------------
# Styling
# ----------------------------
st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-family: Arial, sans-serif;
    }}
    .stApp {{
        background: {CREAM};
    }}
    [data-testid="stSidebar"] {{
        background: {GREEN_DARK};
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    .brand-title {{
        color: {GREEN_DARK};
        font-size: 3.1rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.3rem;
    }}
    .brand-title span {{
        color: {ORANGE};
    }}
    .subtitle {{
        color: {GREEN};
        font-size: 1.25rem;
        margin-bottom: 1.2rem;
    }}
    .hero {{
        padding: 1.2rem 0 0.5rem 0;
    }}
    .section-title {{
        color: {GREEN_DARK};
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0 0.3rem;
    }}
    .muted {{
        color: #61766a;
        font-size: 1rem;
    }}
    .metric-card {{
        background: white;
        border-radius: 22px;
        padding: 1.1rem;
        border: 1px solid rgba(5,64,35,.08);
        box-shadow: 0 8px 25px rgba(5,64,35,.06);
        min-height: 125px;
    }}
    .metric-number {{
        color: {GREEN_DARK};
        font-size: 2rem;
        font-weight: 700;
    }}
    .metric-label {{
        color: #6c7c73;
        font-size: 0.95rem;
    }}
    .recipe-card {{
        background: white;
        border-radius: 24px;
        padding: 0.8rem;
        border: 1px solid rgba(5,64,35,.08);
        box-shadow: 0 8px 25px rgba(5,64,35,.06);
        margin-bottom: 0.7rem;
    }}
    .recipe-name {{
        color: {GREEN_DARK};
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 0.35rem;
    }}
    .badge {{
        display: inline-block;
        padding: 0.28rem 0.55rem;
        border-radius: 999px;
        margin-right: 0.2rem;
        font-size: 0.78rem;
        font-weight: 600;
    }}
    .badge-green {{ background: #e1f1d9; color: {GREEN_DARK}; }}
    .badge-orange {{ background: #fff0e7; color: #a94812; }}
    .badge-yellow {{ background: #fff5d7; color: #7c5a00; }}
    .ingredient-pill {{
        display: inline-block;
        background: #edf7e8;
        color: {GREEN_DARK};
        border-radius: 999px;
        padding: 0.45rem 0.75rem;
        margin: 0.2rem;
        font-weight: 600;
    }}
    .welcome-box {{
        background: rgba(255,255,255,.75);
        border: 1px solid rgba(5,64,35,.08);
        border-radius: 28px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 12px 35px rgba(5,64,35,.07);
    }}
    .chat-bubble {{
        background: white;
        border-radius: 18px;
        padding: 0.9rem 1rem;
        border-left: 5px solid {ORANGE};
        margin: 0.5rem 0;
    }}
    div.stButton > button {{
        border-radius: 14px;
        border: 0;
        background: {GREEN};
        color: white;
        font-weight: 700;
        min-height: 2.6rem;
    }}
    div.stButton > button:hover {{
        background: {GREEN_DARK};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Helpers
# ----------------------------
@st.cache_data
def load_recipes():
    with open(RECIPES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

recipes = load_recipes()

def image_to_bytes(path):
    return Path(path).read_bytes()

def ingredient_html(ingredients):
    return " ".join(
        f'<span class="ingredient-pill">{INGREDIENT_EMOJIS.get(i, "🍴")} {i.title()}</span>'
        for i in ingredients
    )

def matching_score(user_ingredients, recipe):
    user = {x.strip().lower() for x in user_ingredients}
    required = set(recipe["ingredients"])
    if not required:
        return 0
    return round(100 * len(user & required) / len(required))

def get_matches(user_ingredients, limit=6):
    scored = []
    for r in recipes:
        score = matching_score(user_ingredients, r)
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1]["time"]))
    return scored[:limit]

def recipe_card(r, score=None):
    c1, c2 = st.columns([1.05, 1.35])
    with c1:
        st.image(str(ASSETS / "recipes" / f"{r['id']}.png"), use_container_width=True)
    with c2:
        st.markdown(f'<div class="recipe-name">{r["emoji"]} {r["name"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="badge badge-orange">🔥 {r["calories"]} kcal</span>'
            f'<span class="badge badge-yellow">⏱️ {r["time"]} min</span>'
            f'<span class="badge badge-green">🟢 {r["difficulty"]}</span>',
            unsafe_allow_html=True,
        )
        st.write(f"👨‍👩‍👧‍👦 Serves {r['servings']}")
        if score is not None:
            st.progress(score / 100, text=f"Ingredient Match: {score}%")
        st.markdown(ingredient_html(r["ingredients"]), unsafe_allow_html=True)
        fav = r["id"] in st.session_state.favorites
        if st.button("❤️ Remove from Favorites" if fav else "♡ Add to Favorites",
                     key=f"fav_{r['id']}"):
            if fav:
                st.session_state.favorites.remove(r["id"])
            else:
                st.session_state.favorites.add(r["id"])
            st.rerun()
        st.markdown("---")
        st.markdown("**👩🏻‍🍳 Instructions**")
        for i, step in enumerate(r["steps"], 1):
            st.write(f"**{i}.** {step}")

def top_bar():
    left, right = st.columns([4.8, 1.2])
    with left:
        st.markdown(
            '<div class="brand-title">SNAP<span>-BITE</span></div>'
            '<div class="subtitle">Snap • Detect • Cook</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.image(str(ASSETS / "logo.png"), width=110)
        st.markdown(
            f'<div style="text-align:center;color:{GREEN_DARK};font-weight:700;">'
            f'👨🏻‍🍳 Chef {st.session_state.username}</div>',
            unsafe_allow_html=True,
        )

def login():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(str(ASSETS / "logo.png"), width=230)
        st.markdown(
            f'<div style="text-align:center;">'
            f'<div class="brand-title">SNAP<span>-BITE</span></div>'
            f'<div class="subtitle">Where cooking creativity begins.</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("### 👤 Welcome, Chef!")
        username = st.text_input("Username", placeholder="Enter your name")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("🍳 Login", use_container_width=True):
            if username.strip() and password:
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.rerun()
            else:
                st.error("Please enter both username and password.")
        st.caption("Prototype login: accounts are stored only for this session.")

# ----------------------------
# Session state
# ----------------------------
defaults = {
    "logged_in": False,
    "username": "",
    "favorites": set(),
    "detected_ingredients": [],
    "feedback": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.logged_in:
    login()
    st.stop()

# ----------------------------
# Sidebar navigation
# ----------------------------
with st.sidebar:
    st.image(str(ASSETS / "logo.png"), width=120)
    st.markdown(f"### 👨🏻‍🍳 Chef {st.session_state.username}")
    st.caption("Your ingredients. Your ideas. Your bite.")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [
            "🏠 Welcome",
            "📊 Dashboard",
            "📸 Snap / Upload",
            "🎤 Voice",
            "⌨️ Text",
            "🍳 Recipe Explorer",
            "🎲 Surprise Me",
            "🏆 Best Recipes",
            "❤️ Favorites",
            "🤖 Snap-Bite Chef",
            "💬 Feedback",
            "💚 About",
        ],
    )
    st.markdown("---")
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

top_bar()

# ----------------------------
# Pages
# ----------------------------
if page == "🏠 Welcome":
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(str(ASSETS / "snap_bite_intro.gif"), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="welcome-box">'
        '<div class="section-title">Welcome to Snap-Bite! 👋</div>'
        '<div style="font-size:1.55rem;color:#1E6D4A;font-weight:700;">'
        'Where cooking creativity begins.'
        '</div>'
        '<p style="font-size:1.05rem;color:#61766a;">'
        'Turn what you have at home into something delicious.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("🍳 Start Cooking", use_container_width=True):
        st.info("Choose Snap / Upload, Voice, or Text from the left menu.")

elif page == "📊 Dashboard":
    st.markdown('<div class="section-title">Your Kitchen Dashboard 📊</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="muted">Welcome back, Chef {st.session_state.username}!</div>', unsafe_allow_html=True)
    st.write("")
    total_ingredients = len(set(st.session_state.detected_ingredients))
    total_favorites = len(st.session_state.favorites)
    cols = st.columns(4)
    metrics = [
        (total_ingredients, "Ingredients Detected", "🥕"),
        (len(recipes), "Recipes Available", "🍳"),
        (total_favorites, "Favorite Recipes", "❤️"),
        (len(st.session_state.feedback), "Your Feedback", "💬"),
    ]
    for col, (num, label, emoji) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-number">{emoji} {num}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )
    st.write("")
    if st.session_state.detected_ingredients:
        st.markdown("### 🧺 Your Latest Ingredients")
        st.markdown(ingredient_html(st.session_state.detected_ingredients), unsafe_allow_html=True)
        st.markdown("### 💡 Best Matches")
        for score, r in get_matches(st.session_state.detected_ingredients, 3):
            st.markdown(f"**{r['emoji']} {r['name']}** — {score}% ingredient match")
            st.progress(score / 100)
    else:
        st.info("Detect ingredients from a photo or add them from the Text page to personalize your dashboard.")

elif page == "📸 Snap / Upload":
    st.markdown('<div class="section-title">What’s in your fridge? 🧊</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Take a photo or upload an image of your ingredients.</div>', unsafe_allow_html=True)
    camera = st.camera_input("📷 Take a Photo")
    uploaded = st.file_uploader("📁 Or Upload an Image", type=["jpg", "jpeg", "png", "webp"])
    selected = camera if camera is not None else uploaded

    if selected:
        image = Image.open(selected)
        st.image(image, caption="Your kitchen image", use_container_width=True)

        detected = []
        if MODEL_FILE.exists():
            try:
                from ultralytics import YOLO
                model = YOLO(str(MODEL_FILE))
                results = model.predict(image, conf=0.25, verbose=False)
                names = model.names
                for result in results:
                    for cls_id in result.boxes.cls.tolist():
                        name = str(names[int(cls_id)]).lower()
                        detected.append(name)
                detected = list(dict.fromkeys(detected))
            except Exception as e:
                st.warning("YOLO could not run in this environment. Demo ingredient selection is available below.")
        else:
            st.info("YOLO model file not found yet. Add `models/best.pt` after training your custom ingredient model.")

        if detected:
            st.session_state.detected_ingredients = detected
        else:
            demo_options = sorted(INGREDIENT_EMOJIS.keys())
            st.markdown("### 🧪 Demo / Manual Ingredients")
            st.caption("Use this while the trained YOLO model is not connected.")
            chosen = st.multiselect("Select ingredients", demo_options, default=st.session_state.detected_ingredients)
            if chosen:
                st.session_state.detected_ingredients = chosen

        if st.session_state.detected_ingredients:
            st.success(f"🎉 We found {len(st.session_state.detected_ingredients)} ingredients!")
            st.markdown(ingredient_html(st.session_state.detected_ingredients), unsafe_allow_html=True)
            st.markdown("### 🍳 Recipe Ideas")
            for score, r in get_matches(st.session_state.detected_ingredients, 5):
                with st.container(border=True):
                    recipe_card(r, score)

elif page == "🎤 Voice":
    st.markdown('<div class="section-title">Tell us what you have 🎤</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Record your ingredients, then confirm the words you said.</div>', unsafe_allow_html=True)
    audio = st.audio_input("🎙️ Record your ingredients")
    if audio:
        st.audio(audio)
        st.info("Voice recording is ready. For this prototype, type the transcript below; later you can connect a speech-to-text model.")
    transcript = st.text_input("What did you say?", placeholder="Example: eggs, tomato, cheese and bread")
    if st.button("🔎 Find My Ingredients"):
        words = [x.strip().lower() for x in transcript.replace(" and ", ",").split(",") if x.strip()]
        words = [x for x in words if x in INGREDIENT_EMOJIS]
        st.session_state.detected_ingredients = list(dict.fromkeys(words))
        if words:
            st.success("✨ Ingredients understood!")
            st.markdown(ingredient_html(words), unsafe_allow_html=True)
        else:
            st.warning("Try using ingredient names such as eggs, tomato, cheese, chicken, rice or bread.")

elif page == "⌨️ Text":
    st.markdown('<div class="section-title">Type your ingredients ✍🏻</div>', unsafe_allow_html=True)
    text = st.text_area("Ingredients", placeholder="Example: eggs, tomato, cheese, bread", height=130)
    if st.button("🍳 Find Recipes"):
        words = [x.strip().lower() for x in text.replace("\n", ",").replace(" and ", ",").split(",") if x.strip()]
        words = [x for x in words if x in INGREDIENT_EMOJIS]
        st.session_state.detected_ingredients = list(dict.fromkeys(words))
        if words:
            st.success(f"Found {len(words)} ingredients!")
            st.markdown(ingredient_html(words), unsafe_allow_html=True)
            st.markdown("### 💡 Your Best Matches")
            for score, r in get_matches(words, 6):
                with st.container(border=True):
                    recipe_card(r, score)
        else:
            st.warning("No matching ingredients found. Try simple names such as tomato, egg, milk or cheese.")

elif page == "🍳 Recipe Explorer":
    st.markdown('<div class="section-title">Explore Recipes 🍴</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Search, filter, and find your next bite.</div>', unsafe_allow_html=True)
    query = st.text_input("🔎 Search recipes", placeholder="Search by recipe or ingredient...")
    categories = ["All"] + sorted(set(r["category"] for r in recipes))
    category = st.selectbox("🌍 Category", categories)
    c1, c2, c3 = st.columns(3)
    with c1:
        max_cal = st.slider("🔥 Max Calories", 100, 800, 800, 50)
    with c2:
        max_time = st.slider("⏱️ Max Time (minutes)", 5, 90, 90, 5)
    with c3:
        difficulty = st.selectbox("🟢 Difficulty", ["All", "Easy", "Medium", "Hard"])

    filtered = recipes
    if query:
        q = query.lower()
        filtered = [r for r in filtered if q in r["name"].lower() or any(q in x for x in r["ingredients"])]
    if category != "All":
        filtered = [r for r in filtered if r["category"] == category]
    filtered = [r for r in filtered if r["calories"] <= max_cal and r["time"] <= max_time]
    if difficulty != "All":
        filtered = [r for r in filtered if r["difficulty"] == difficulty]

    st.write(f"**{len(filtered)} recipes found**")
    cols = st.columns(3)
    for i, r in enumerate(filtered):
        with cols[i % 3]:
            st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
            st.image(str(ASSETS / "recipes" / f"{r['id']}.png"), use_container_width=True)
            st.markdown(f'<div class="recipe-name">{r["emoji"]} {r["name"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<span class="badge badge-orange">🔥 {r["calories"]}</span>'
                f'<span class="badge badge-yellow">⏱️ {r["time"]}m</span>'
                f'<span class="badge badge-green">🟢 {r["difficulty"]}</span>',
                unsafe_allow_html=True,
            )
            st.write(f"👨‍👩‍👧‍👦 Serves {r['servings']}")
            st.markdown(ingredient_html(r["ingredients"]), unsafe_allow_html=True)
            if st.button("View Recipe", key=f"view_{r['id']}"):
                st.session_state.selected_recipe = r["id"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if "selected_recipe" in st.session_state:
        chosen = next((r for r in recipes if r["id"] == st.session_state.selected_recipe), None)
        if chosen:
            st.markdown("---")
            st.markdown("## 🍽️ Recipe Details")
            recipe_card(chosen)

elif page == "🎲 Surprise Me":
    st.markdown('<div class="section-title">🎲 Surprise Me!</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Not sure what to cook? Let Snap-Bite choose.</div>', unsafe_allow_html=True)
    if st.button("✨ Give Me a Surprise Recipe", use_container_width=True):
        if st.session_state.detected_ingredients:
            matches = get_matches(st.session_state.detected_ingredients, 10)
            chosen = random.choice([r for _, r in matches]) if matches else random.choice(recipes)
        else:
            chosen = random.choice(recipes)
        st.session_state.surprise = chosen["id"]
    if "surprise" in st.session_state:
        r = next(x for x in recipes if x["id"] == st.session_state.surprise)
        st.markdown("### Your surprise recipe is... 🎉")
        with st.container(border=True):
            recipe_card(r, matching_score(st.session_state.detected_ingredients, r) if st.session_state.detected_ingredients else None)
        st.success("Enjoy your bite! 🍴💚")

elif page == "🏆 Best Recipes":
    st.markdown('<div class="section-title">🏆 Snap-Bite Picks</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Useful labels instead of made-up user ratings.</div>', unsafe_allow_html=True)
    tabs = st.tabs(["⚡ Quick", "🥗 Healthy", "🔥 Low Calories", "💚 Best Match"])
    with tabs[0]:
        data = sorted(recipes, key=lambda r: r["time"])[:6]
    with tabs[1]:
        data = [r for r in recipes if r["category"] == "Healthy"][:6]
    with tabs[2]:
        data = sorted(recipes, key=lambda r: r["calories"])[:6]
    with tabs[3]:
        data = [r for _, r in get_matches(st.session_state.detected_ingredients, 6)] if st.session_state.detected_ingredients else recipes[:6]
    cols = st.columns(3)
    for i, r in enumerate(data):
        with cols[i % 3]:
            st.image(str(ASSETS / "recipes" / f"{r['id']}.png"), use_container_width=True)
            st.markdown(f"**{r['emoji']} {r['name']}**")
            st.caption(f"🔥 {r['calories']} kcal • ⏱️ {r['time']} min • 🟢 {r['difficulty']}")

elif page == "❤️ Favorites":
    st.markdown('<div class="section-title">Your Favorites ❤️</div>', unsafe_allow_html=True)
    favs = [r for r in recipes if r["id"] in st.session_state.favorites]
    if not favs:
        st.info("You have no favorite recipes yet. Add one from Recipe Explorer.")
    else:
        for r in favs:
            with st.container(border=True):
                recipe_card(r)

elif page == "🤖 Snap-Bite Chef":
    st.markdown('<div class="section-title">Snap-Bite Chef 🤖👩🏻‍🍳</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">A simple local cooking assistant for the prototype.</div>', unsafe_allow_html=True)
    prompt = st.chat_input("Ask me about your ingredients or a recipe...")
    if prompt:
        st.chat_message("user").write(prompt)
        p = prompt.lower()
        ingredients = st.session_state.detected_ingredients

        if "what can i cook" in p or "what should i cook" in p:
            if ingredients:
                matches = get_matches(ingredients, 3)
                answer = "Based on your ingredients, try: " + ", ".join(r["name"] for _, r in matches)
            else:
                answer = "Add ingredients from Snap / Upload, Voice, or Text first."
        elif "instead of" in p or "substitute" in p or "alternative" in p:
            answer = "Try a similar ingredient with a close texture or flavor. For example, milk can often be replaced with yogurt in some sauces."
        elif "healthy" in p:
            answer = "Try reducing oil, adding vegetables, and choosing grilled or baked ingredients."
        elif "15" in p or "quick" in p:
            quick = sorted([r for r in recipes if r["time"] <= 15], key=lambda r: r["time"])[:3]
            answer = "Quick picks: " + ", ".join(r["name"] for r in quick)
        else:
            answer = "I can help you find recipes, suggest alternatives, and choose quick or healthier meals."
        st.chat_message("assistant").write(answer)

elif page == "💬 Feedback":
    st.markdown('<div class="section-title">What do you think? 💚</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Your feedback helps us make Snap-Bite better.</div>', unsafe_allow_html=True)
    rating = st.feedback("stars")
    liked = st.multiselect("What did you like?", ["Easy to use", "Recipe ideas", "Design", "Ingredient detection", "Fast"])
    comment = st.text_area("Tell us more", placeholder="Write your feedback...")
    if st.button("💚 Submit Feedback"):
        st.session_state.feedback.append({
            "rating": rating,
            "liked": liked,
            "comment": comment,
        })
        st.success("Thank you for your feedback! 💚")
    if st.session_state.feedback:
        st.markdown("### Recent feedback in this session")
        for item in st.session_state.feedback[-3:]:
            stars = "⭐" * ((item["rating"] + 1) if item["rating"] is not None else 0)
            st.markdown(f'<div class="chat-bubble">{stars}<br>{item["comment"]}</div>', unsafe_allow_html=True)

elif page == "💚 About":
    st.markdown('<div class="section-title">Our Story 💚</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="welcome-box">
        <h2 style="color:#054023;">Cooking should be creative, not stressful.</h2>
        <p style="color:#61766a;font-size:1.05rem;">
        Snap-Bite helps home cooks turn the ingredients they already have
        into simple and delicious meal ideas.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    cols = st.columns(3)
    for col, num, label in zip(
        cols,
        [len(recipes), len(set(x["category"] for x in recipes)), len(set(i for r in recipes for i in r["ingredients"]))],
        ["Recipe Ideas", "Food Categories", "Ingredient Types"],
    ):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-number">{num}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("### ✨ Snap • Detect • Cook")
    st.write("Your ingredients. Your ideas. Your bite.")
