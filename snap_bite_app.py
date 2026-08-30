import re
import random
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

# Optional YOLO dependency is required in deployment; keep import lazy so the app
# can still render recipes if the model package is temporarily unavailable.

st.set_page_config(
    page_title="Snap-Bite",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
IMAGES = BASE_DIR / "images"
LOGO_FILE = BASE_DIR / "logo.png"
GIF_FILE = BASE_DIR / "snap_bite_intro.gif"
RECIPES_FILE = BASE_DIR / "recipes.xlsx"
MODEL_FILE = BASE_DIR / "best.pt"

GREEN_DARK = "#054023"
GREEN = "#1E6D4A"
LEAF = "#A5D08C"
YELLOW = "#F6B454"
ORANGE = "#FD893E"
CREAM = "#F9EFDE"
WHITE = "#FFFFFF"
MUTED = "#61766A"

CATEGORY_LABELS = {
    "Breakfast": "Breakfast",
    "Main Dishes": "Main Dishes",
    "Soups": "Soups",
    "Appetizers & Snacks": "Appetizers & Snacks",
    "Desserts": "Desserts",
    "Drinks": "Drinks",
}

# Cuisine mapping follows the cuisine assignments agreed for the recipe list.
CUISINE_BY_NAME = {
    "Pancakes":"American","French Toast":"American","Shakshuka":"Arabic","Classic Omelette":"International","Avocado Toast":"American",
    "Breakfast Burrito":"Mexican","Foul Medames":"Arabic","Balaleet":"Gulf","Egg & Cheese Sandwich":"American","Overnight Oats":"International",
    "Scrambled Eggs":"International","Egg Muffins":"American","Turkish Eggs (Cilbir)":"Turkish","Menemen":"Turkish","Banana Oat Pancakes":"International",
    "French Omelette":"French","Breakfast Quesadilla":"Mexican","Spinach & Cheese Omelette":"International","Masala Omelette":"Indian","Breakfast Croissant":"French",
    "Egg & Avocado Bowl":"International","Greek Yogurt & Granola Bowl":"Greek","Banana French Toast":"American","Cheese Manakish":"Lebanese","Zaatar Manakish":"Lebanese",
    "Chicken Machboos":"Gulf","Chicken Mandi":"Gulf","Chicken Kabsa":"Gulf","Chicken Shawarma":"Arabic","Koshari":"Egyptian","Chicken Kofta":"Arabic",
    "Beef Kofta":"Arabic","Mujaddara":"Arabic","Stuffed Grape Leaves":"Arabic","Spaghetti Bolognese":"Italian","Chicken Alfredo":"Italian","Lasagna":"Italian",
    "Margherita Pizza":"Italian","Chicken Pesto Pasta":"Italian","Chicken Tacos":"Mexican","Beef Tacos":"Mexican","Chicken Quesadilla":"Mexican",
    "Beef Burrito":"Mexican","Chicken Fajitas":"Mexican","Cheeseburger":"American","Chicken Burger":"American","Club Sandwich":"American",
    "Chicken Caesar Salad":"American","Chicken Biryani":"Indian","Meat Machboos":"Gulf","Butter Chicken":"Indian","Meat Kabsa":"Gulf",
    "Beef Mandi":"Gulf","Harees":"Gulf","Thareed":"Gulf","Fatteh":"Arabic","Chicken Musakhan":"Palestinian","Maqluba":"Arabic",
    "Beef Shawarma":"Arabic","Chicken Tagine":"Moroccan","Chicken Parmesan":"Italian","Mushroom Risotto":"Italian","Ravioli with Tomato Sauce":"Italian",
    "Gnocchi with Tomato Sauce":"Italian","Chicken Pizza":"Italian","Beef Enchiladas":"Mexican","Chicken Enchiladas":"Mexican","Chicken Tostadas":"Mexican",
    "Mexican Rice Bowl":"Mexican","Chicken Wings":"American","BBQ Chicken":"American","Chicken Pot Pie":"American","Mac & Cheese":"American",
    "Loaded Baked Potato":"American","Chicken Teriyaki":"Japanese","Beef Stir-Fry":"Asian","Chicken Fried Rice":"Asian","Beef Fried Rice":"Asian",
    "Chicken Pad Thai":"Thai","Thai Green Curry":"Thai","Grilled Chicken Salad":"International","Tuna Salad":"International","Chicken Wrap":"International",
    "Quinoa Bowl":"International","Grilled Chicken & Vegetables":"International","Baked Salmon with Vegetables":"International","Chickpea Salad":"Mediterranean","Hummus Bowl":"Middle Eastern",
    "Mediterranean Pasta Salad":"Mediterranean","Greek Chicken Salad":"Greek","Salmon Avocado Bowl":"International","Chicken Quinoa Bowl":"International","Lentil & Vegetable Bowl":"Middle Eastern",
    "Tuna Avocado Bowl":"International","Grilled Vegetable Wrap":"Mediterranean","Baked Falafel Bowl":"Middle Eastern","Mediterranean Couscous Bowl":"Mediterranean","Chicken & Sweet Potato Bowl":"International",
    "Egg & Quinoa Salad":"International","Grilled Fish & Rice Bowl":"Mediterranean","Tomato Soup":"International","Chicken Soup":"International","Lentil Soup":"Middle Eastern",
    "Creamy Mushroom Soup":"International","Chicken Noodle Soup":"American","Vegetable Soup":"International","Pumpkin Soup":"International","Broccoli Cheddar Soup":"American",
    "Minestrone Soup":"Italian","French Onion Soup":"French","Chicken Corn Soup":"Asian","Hot & Sour Soup":"Chinese","Seafood Chowder":"American",
    "Harira Soup":"Moroccan","Mushroom & Potato Soup":"International","Falafel":"Arabic","Hummus":"Middle Eastern","Baba Ghanoush":"Middle Eastern",
    "Muhammara":"Syrian","Sambousek":"Arabic","Chicken Samosa":"Indian","Beef Samosa":"Indian","Vegetable Spring Rolls":"Asian",
    "Chicken Spring Rolls":"Asian","Bruschetta":"Italian","Garlic Bread":"Italian","Caprese Skewers":"Italian","Mozzarella Sticks":"American",
    "Chicken Skewers":"Mediterranean","Beef Kebabs":"Middle Eastern","Stuffed Mushrooms":"American","Potato Wedges":"American","Cheese Quesadilla Bites":"Mexican",
    "Guacamole & Tortilla Chips":"Mexican","Baked Chicken Tenders":"American","Popcorn":"American","Chocolate Energy Bites":"International","Peanut Butter Energy Balls":"American",
    "Granola Bars":"International","Apple & Peanut Butter":"American","Yogurt & Berries":"International","Fruit Salad":"International","Trail Mix":"American",
    "Baked Sweet Potato Fries":"American","Cinnamon Apple Chips":"American","Banana Chips":"International","Roasted Chickpeas":"Middle Eastern","Cheese & Crackers":"International",
    "Spicy Lebanese Potatoes":"Lebanese","Mini Pizza Bites":"Italian","Mutabbal":"Middle Eastern","Date & Nut Bites":"Middle Eastern","Coconut Energy Balls":"International",
    "Baked Tortilla Chips":"Mexican","Cucumber & Yogurt Bites":"Mediterranean","Chocolate Cake":"American","Cheesecake":"American","Brownies":"American",
    "Chocolate Chip Cookies":"American","Fruit Parfait":"International","Tiramisu":"Italian","Baklava":"Arabic","Umm Ali":"Egyptian","Rice Pudding":"Arabic",
    "Kunafa":"Arabic","Chocolate Mousse":"French","Creme Brulee":"French","Apple Pie":"American","Carrot Cake":"American","Banana Bread":"American",
    "Red Velvet Cake":"American","Cinnamon Rolls":"American","Lemon Cake":"International","Mango Cheesecake":"International","Fateer":"Egyptian","Date Cake":"Middle Eastern",
    "Basbousa":"Middle Eastern","Maamoul":"Arabic","Mahalabia":"Arabic","Coconut Pudding":"International","Mango Smoothie":"International","Strawberry Smoothie":"International",
    "Banana Smoothie":"International","Berry Smoothie":"International","Green Smoothie":"International","Chocolate Milkshake":"American","Vanilla Milkshake":"American",
    "Strawberry Milkshake":"American","Iced Coffee":"International","Iced Matcha Latte":"Japanese","Acai":"Brazilian","Mint Lemonade":"Middle Eastern",
    "Mango Lassi":"Indian","Strawberry Lassi":"Indian","Arabic Mint Tea":"Middle Eastern","Karak Tea":"Gulf","Hot Chocolate":"International","Fresh Orange Juice":"International",
    "Watermelon Juice":"International","Date Milkshake":"Gulf",
}

st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{ font-family: Arial, sans-serif; }}
    .stApp {{ background: {CREAM}; }}
    [data-testid="stSidebar"] {{ background: {GREEN_DARK}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .brand-title {{ color:{GREEN_DARK}; font-size:2.8rem; font-weight:800; line-height:1; }}
    .brand-title span {{ color:{GREEN_DARK}; }}
    .subtitle {{ color:{GREEN}; font-size:1.05rem; margin-top:.35rem; }}
    .section-title {{ color:{GREEN_DARK}; font-size:2rem; font-weight:800; margin:.35rem 0; }}
    .muted {{ color:{MUTED}; font-size:1rem; }}
    .welcome-left {{ background:{GREEN_DARK}; color:white; border-radius:28px 0 0 28px; padding:3.1rem; min-height:470px; display:flex; flex-direction:column; justify-content:center; }}
    .welcome-right {{ background:{CREAM}; border:1px solid rgba(5,64,35,.08); border-left:0; border-radius:0 28px 28px 0; padding:2rem; min-height:470px; display:flex; flex-direction:column; justify-content:center; }}
    .welcome-title {{ font-size:2.25rem; font-weight:800; margin:0 0 .5rem; }}
    .welcome-copy {{ font-size:1.18rem; line-height:1.6; margin:.3rem 0 1.4rem; }}
    .welcome-gif {{ max-width:520px; margin:0 auto .8rem auto; text-align:center; }}
    .welcome-content {{ text-align:center; max-width:820px; margin:0 auto 2rem auto; }}
    .welcome-wordmark {{ color:{GREEN_DARK}; font-size:3.0rem; font-weight:900; letter-spacing:.06em; line-height:1; margin-top:.3rem; }}
    .welcome-tagline {{ color:{GREEN}; font-size:1.1rem; font-weight:700; margin:.55rem 0 1.1rem; }}
    .welcome-title {{ color:{GREEN_DARK}; font-size:2.25rem; font-weight:800; margin:0 0 .45rem; }}
    .welcome-subtitle {{ color:{GREEN}; font-size:1.35rem; margin:.2rem 0 .55rem; }}
    .card {{ background:white; border:1px solid rgba(5,64,35,.08); border-radius:22px; padding:1rem; box-shadow:0 8px 24px rgba(5,64,35,.06); margin-bottom:1rem; }}
    .recipe-name {{ color:{GREEN_DARK}; font-size:1.3rem; font-weight:800; margin:.3rem 0 .55rem; }}
    .tag {{ display:inline-block; border-radius:999px; padding:.25rem .55rem; margin:0 .2rem .25rem 0; font-size:.78rem; font-weight:700; }}
    .tag-g {{ background:#e2f2dc; color:{GREEN_DARK}; }}
    .tag-o {{ background:#fff0e6; color:#9a4210; }}
    .tag-y {{ background:#fff4d1; color:#725400; }}
    .tag-b {{ background:#e9f1ff; color:#2e4f7f; }}
    .metric-card {{ background:white; border:1px solid rgba(5,64,35,.08); border-radius:20px; padding:1.15rem; box-shadow:0 8px 22px rgba(5,64,35,.05); min-height:120px; }}
    .metric-num {{ color:{GREEN_DARK}; font-size:1.8rem; font-weight:800; }}
    .metric-label {{ color:#718077; font-size:.9rem; margin-top:.25rem; }}
    .ingredient-row {{ background:#f0f8eb; border-radius:14px; padding:.65rem .8rem; margin:.35rem 0; color:{GREEN_DARK}; font-weight:600; }}
    .step-row {{ padding:.6rem .75rem; border-left:4px solid {GREEN}; background:#fff; border-radius:10px; margin:.35rem 0; }}
    .story-box {{ background:white; border:1px solid rgba(5,64,35,.08); border-radius:26px; padding:1.7rem; box-shadow:0 10px 30px rgba(5,64,35,.06); }}
    div.stButton > button {{ border-radius:14px; border:0; background:{GREEN}; color:white; font-weight:800; min-height:2.7rem; }}
    div.stButton > button:hover {{ background:{GREEN_DARK}; color:white; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def _clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


@st.cache_data

def load_recipes():
    df = pd.read_excel(RECIPES_FILE)
    # Accept the user's current workbook while making the app tolerant of later edits.
    required = {"Recipe_ID", "Dish_Name_English", "Category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required Excel columns: {', '.join(sorted(missing))}")
    records = []
    for _, row in df.iterrows():
        rid = int(row["Recipe_ID"])
        name = _clean_text(row["Dish_Name_English"])
        category = _clean_text(row["Category"])
        cuisine = _clean_text(row.get("Cuisine", "")) or CUISINE_BY_NAME.get(name, "International")
        servings = int(float(row.get("Servings", 2) or 2)) if _clean_text(row.get("Servings", "")) else 2
        calories = float(row.get("Calories_per_Serving", 0) or 0)
        prep = float(row.get("Prep_Time_Min", 0) or 0)
        cook = float(row.get("Cook_Time_Min", 0) or 0)
        difficulty = _clean_text(row.get("Difficulty", "Medium")) or "Medium"
        ingredients_raw = _clean_text(row.get("Ingredients", ""))
        ingredients = [x.strip() for x in re.split(r"[;\n]+", ingredients_raw) if x.strip()]
        instructions_raw = _clean_text(row.get("Instructions", ""))
        steps = [x.strip() for x in re.split(r"(?=\d+\.\s)", instructions_raw) if x.strip()]
        oven_temp = _clean_text(row.get("Oven_Temperature_C", ""))
        oven_time = _clean_text(row.get("Oven_Time_Min", ""))
        serving = _clean_text(row.get("Serving_Suggestion", ""))
        total_time = int(round(prep + cook)) if prep or cook else 0
        records.append({
            "id": rid, "name": name, "category": category, "cuisine": cuisine,
            "servings": servings, "calories": calories, "prep": prep, "cook": cook,
            "time": total_time, "difficulty": difficulty, "ingredients": ingredients,
            "steps": steps, "oven_temp": oven_temp, "oven_time": oven_time, "serving": serving,
        })
    return records


recipes = load_recipes()


def find_recipe_image(recipe_id):
    matches = []
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"):
        matches.extend(IMAGES.glob(f"{recipe_id:03d}_*{ext}"))
    # Fallback for exact numeric prefix regardless of punctuation/extension.
    if not matches:
        matches = [p for p in IMAGES.iterdir() if p.is_file() and p.stem.startswith(f"{recipe_id:03d}_")]
    return sorted(matches)[0] if matches else None


def parse_leading_number(text):
    s = text.strip()
    match = re.match(r"^(\d+(?:\.\d+)?|\d+\s*/\s*\d+)", s)
    if not match:
        return None
    token = match.group(1).replace(" ", "")
    if "/" in token:
        a, b = token.split("/", 1)
        return float(a) / float(b)
    return float(token)


def scale_ingredient(text, factor):
    num = parse_leading_number(text)
    if num is None or factor == 1:
        return text
    scaled = num * factor
    if abs(scaled - round(scaled)) < 1e-9:
        shown = str(int(round(scaled)))
    else:
        shown = f"{scaled:.2f}".rstrip("0").rstrip(".")
    return re.sub(r"^(\d+(?:\.\d+)?|\d+\s*/\s*\d+)", shown, text.strip(), count=1)


def normalize_token(text):
    s = text.lower().strip()
    s = s.replace("_", " ")
    aliases = {
        "chicken breast": "chicken", "chicken thigh": "chicken", "chicken wing": "chicken",
        "bell pepper": "pepper", "red rice": "rice", "white rice": "rice",
        "egg_": "egg", "pork belly": "pork", "lobster tails": "lobster", "sea scallops": "scallop",
    }
    return aliases.get(s, s)


def recipe_tokens(recipe):
    tokens = set()
    for ing in recipe["ingredients"]:
        clean = ing.lower()
        for token in [
            "chicken", "beef", "rice", "onion", "tomato", "egg", "avocado", "bread", "milk", "cheese",
            "flour", "banana", "strawberry", "potato", "carrot", "mushroom", "broccoli", "spinach",
            "pasta", "tortilla", "yogurt", "lemon", "garlic", "olive oil", "chickpeas", "tuna",
            "salmon", "shrimp", "peas", "bell pepper", "pepper", "corn", "ginger", "cucumber", "cocoa",
            "butter", "cream", "honey", "noodles", "vermicelli", "sugar", "peanuts", "coconut", "dates",
        ]:
            if token in clean:
                tokens.add(normalize_token(token))
    return tokens


def score_match(user_ingredients, recipe):
    user = {normalize_token(x) for x in user_ingredients}
    required = recipe_tokens(recipe)
    if not required:
        return 0
    return round(100 * len(user & required) / len(required))


def get_matches(user_ingredients, limit=12):
    scored = [(score_match(user_ingredients, r), r) for r in recipes]
    scored = [x for x in scored if x[0] > 0]
    scored.sort(key=lambda x: (-x[0], x[1]["time"], x[1]["calories"]))
    return scored[:limit]


def render_image(path, caption=None, width=None):
    if not path:
        st.markdown('<div class="card" style="text-align:center;font-size:4rem">🍽️</div>', unsafe_allow_html=True)
        return
    st.image(str(path), caption=caption, width=width, use_container_width=width is None)


def recipe_card(recipe, show_match=None):
    with st.container(border=True):
        cols = st.columns([1.05, 1.35])
        with cols[0]:
            render_image(find_recipe_image(recipe["id"]))
        with cols[1]:
            st.markdown(f'<div class="recipe-name">{recipe["name"]}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<span class="tag tag-b">{recipe["category"]}</span>'
                f'<span class="tag tag-g">{recipe["cuisine"]}</span>'
                f'<span class="tag tag-o">🔥 {int(recipe["calories"])} kcal</span>'
                f'<span class="tag tag-y">⏱️ {recipe["time"]} min</span>'
                f'<span class="tag tag-g">⭐ {recipe["difficulty"]}</span>',
                unsafe_allow_html=True,
            )
            st.write(f"👥 Serves {recipe['servings']}")
            if show_match is not None:
                st.progress(show_match / 100, text=f"Ingredient Match: {show_match}%")
            preview = recipe["ingredients"][:4]
            if preview:
                st.markdown("**Ingredients**")
                for ing in preview:
                    st.write(f"• {ing}")
            if len(recipe["ingredients"]) > 4:
                st.caption(f"+ {len(recipe['ingredients']) - 4} more ingredients")
            if st.button("View Recipe", key=f"view_{recipe['id']}"):
                st.session_state.selected_recipe_id = recipe["id"]
                st.session_state.nav = "🍳 Recipes"
                st.rerun()


def render_recipe_detail(recipe):
    st.markdown(f'<div class="section-title">{recipe["name"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="tag tag-b">{recipe["category"]}</span>'
        f'<span class="tag tag-g">{recipe["cuisine"]}</span>'
        f'<span class="tag tag-o">🔥 {int(recipe["calories"])} kcal / serving</span>'
        f'<span class="tag tag-y">⏱️ {recipe["time"]} min</span>'
        f'<span class="tag tag-g">⭐ {recipe["difficulty"]}</span>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.0, 1.15])
    with left:
        render_image(find_recipe_image(recipe["id"]))
        st.markdown("### 👥 Servings")
        servings = st.number_input("Number of people", min_value=1, max_value=20, value=max(1, recipe["servings"]), step=1, key=f"servings_{recipe['id']}")
        factor = servings / recipe["servings"]
        st.caption("Ingredient quantities update automatically.")
        st.markdown("### 🥕 Ingredients")
        for ing in recipe["ingredients"]:
            st.markdown(f'<div class="ingredient-row">{scale_ingredient(ing, factor)}</div>', unsafe_allow_html=True)
    with right:
        if recipe["prep"] or recipe["cook"]:
            st.markdown(f"**Prep:** {int(recipe['prep'])} min  ·  **Cook:** {int(recipe['cook'])} min")
        if recipe["oven_temp"] and recipe["oven_time"]:
            st.info(f"🔥 Oven: {recipe['oven_temp']}°C for {recipe['oven_time']} minutes")
        st.markdown("### 👨‍🍳 Instructions")
        for i, step in enumerate(recipe["steps"], 1):
            clean = re.sub(r"^\d+\.\s*", "", step)
            st.markdown(f'<div class="step-row"><b>{i}.</b> {clean}</div>', unsafe_allow_html=True)
        if recipe["serving"]:
            st.markdown("### 🍽️ Serving Suggestion")
            st.write(recipe["serving"])
        st.markdown("### ❤️")
        st.markdown("**Enjoy your meal!**")
    if st.button("← Back to Recipes", key=f"back_{recipe['id']}"):
        st.session_state.selected_recipe_id = None
        st.rerun()


# Session state
if "nav" not in st.session_state:
    st.session_state.nav = "🏠 Welcome"
if "selected_recipe_id" not in st.session_state:
    st.session_state.selected_recipe_id = None
if "detected_ingredients" not in st.session_state:
    st.session_state.detected_ingredients = []

# Sidebar
with st.sidebar:
    st.image(str(LOGO_FILE), width=125)
    st.markdown("### Snap-Bite")
    st.caption("Your ingredients. Your ideas. Your bite.")
    st.markdown("---")
    st.radio(
        "Navigation",
        ["🏠 Welcome", "📸 Snap / Upload", "🍳 Recipes", "🎲 Surprise Me", "💚 Our Story + Dashboard"],
        key="nav",
    )

# Top brand bar: logo is intentionally on the LEFT only.
brand_left, brand_right = st.columns([5, 1])
with brand_left:
    st.markdown('<div class="brand-title">SNAP-BITE</div><div class="subtitle">Snap • Detect • Cook</div>', unsafe_allow_html=True)
with brand_right:
    # Keep this blank: the user asked to remove the logo from the top-right.
    st.empty()

page = st.session_state.nav

if page == "🏠 Welcome":
    st.markdown('<div class="welcome-gif">', unsafe_allow_html=True)
    st.image(str(GIF_FILE), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="welcome-content">
            <div class="welcome-wordmark">SNAP-BITE</div>
            <div class="welcome-tagline">Snap • Detect • Cook</div>
            <div class="welcome-title">Welcome to Snap-Bite! 👋</div>
            <div class="welcome-subtitle"><strong>Where cooking creativity begins.</strong></div>
            <div class="welcome-copy">Turn what you have at home into something delicious.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif page == "📸 Snap / Upload":
    st.markdown('<div class="section-title">What’s in your fridge? 🧊</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Take a photo or upload an image of your ingredients.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        camera = st.camera_input("📷 Take a Photo")
    with c2:
        uploaded = st.file_uploader("📁 Upload an Image", type=["jpg", "jpeg", "png", "webp"])
    selected = camera if camera is not None else uploaded
    if selected:
        image = Image.open(selected)
        st.markdown("### Your Image")
        st.image(image, use_container_width=True)
        detected = []

        @st.cache_resource
        def load_yolo_model(model_path):
            from ultralytics import YOLO
            return YOLO(str(model_path))

        if not MODEL_FILE.exists():
            st.error("best.pt was not found. Put best.pt in the same folder as app.py.")
        else:
            try:
                model = load_yolo_model(MODEL_FILE)
                results = model.predict(source=image, conf=0.20, verbose=False)
                names = model.names
                for result in results:
                    if result.boxes is not None and len(result.boxes) > 0:
                        for cls_id in result.boxes.cls.tolist():
                            detected.append(str(names[int(cls_id)]).lower())
                detected = list(dict.fromkeys(detected))
            except Exception as e:
                st.error(f"Model error: {e}")

        if detected:
            st.session_state.detected_ingredients = detected
            st.success(f"Found {len(detected)} ingredients!")
        else:
            st.info("No ingredients were detected. You can select the ingredients manually below.")
        all_known = sorted(set(st.session_state.detected_ingredients))
        selected_ingredients = st.multiselect(
            "Detected ingredients — adjust if needed",
            options=sorted(set(all_known) | {"chicken", "rice", "egg", "tomato", "onion", "cheese", "potato", "milk", "bread", "avocado"}),
            default=all_known,
        )
        if selected_ingredients:
            st.session_state.detected_ingredients = selected_ingredients
            st.success(f"Found {len(selected_ingredients)} ingredients.")
            matches = get_matches(selected_ingredients, 6)
            st.markdown("### 🍳 Recommended Recipes")
            if matches:
                for score, recipe in matches:
                    recipe_card(recipe, show_match=score)
            else:
                st.info("No matching recipes found yet. Try adding or correcting ingredients.")

elif page == "🍳 Recipes":
    st.markdown('<div class="section-title">Explore Recipes 🍴</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Search and filter your next bite.</div>', unsafe_allow_html=True)
    selected_id = st.session_state.selected_recipe_id
    if selected_id:
        recipe = next((r for r in recipes if r["id"] == selected_id), None)
        if recipe:
            render_recipe_detail(recipe)
        else:
            st.session_state.selected_recipe_id = None
    else:
        query = st.text_input("🔎 Search recipes or ingredients", placeholder="e.g. chicken, pasta, soup...")
        f1, f2, f3, f4, f5 = st.columns(5)
        with f1:
            category = st.selectbox("Category", ["All"] + sorted(set(r["category"] for r in recipes)))
        with f2:
            cuisine = st.selectbox("Cuisine", ["All"] + sorted(set(r["cuisine"] for r in recipes)))
        with f3:
            max_cal = st.slider("Max Calories", 50, max(1000, int(max(r["calories"] for r in recipes))), max(1000, int(max(r["calories"] for r in recipes))), 50)
        with f4:
            max_time = st.slider("Max Time (min)", 1, max(180, max(r["time"] for r in recipes)), max(180, max(r["time"] for r in recipes)), 5)
        with f5:
            difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
        servings_filter = st.selectbox("Servings", ["All", "1", "2", "3-4", "5+"])

        filtered = recipes
        if query:
            q = query.lower()
            filtered = [r for r in filtered if q in r["name"].lower() or any(q in x.lower() for x in r["ingredients"])]
        if category != "All":
            filtered = [r for r in filtered if r["category"] == category]
        if cuisine != "All":
            filtered = [r for r in filtered if r["cuisine"] == cuisine]
        filtered = [r for r in filtered if r["calories"] <= max_cal and r["time"] <= max_time]
        if difficulty != "All":
            filtered = [r for r in filtered if r["difficulty"] == difficulty]
        if servings_filter == "1":
            filtered = [r for r in filtered if r["servings"] == 1]
        elif servings_filter == "2":
            filtered = [r for r in filtered if r["servings"] == 2]
        elif servings_filter == "3-4":
            filtered = [r for r in filtered if 3 <= r["servings"] <= 4]
        elif servings_filter == "5+":
            filtered = [r for r in filtered if r["servings"] >= 5]

        st.write(f"**{len(filtered)} recipes found**")
        page_size = 12
        pages = max(1, (len(filtered) + page_size - 1) // page_size)
        current_page = st.number_input("Page", min_value=1, max_value=pages, value=1, step=1)
        shown = filtered[(current_page - 1) * page_size : current_page * page_size]
        cols = st.columns(3)
        for i, recipe in enumerate(shown):
            with cols[i % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                render_image(find_recipe_image(recipe["id"]))
                st.markdown(f'<div class="recipe-name">{recipe["name"]}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<span class="tag tag-b">{recipe["category"]}</span>'
                    f'<span class="tag tag-g">{recipe["cuisine"]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<span class="tag tag-o">🔥 {int(recipe["calories"])} kcal</span>'
                    f'<span class="tag tag-y">⏱️ {recipe["time"]} min</span>'
                    f'<span class="tag tag-g">⭐ {recipe["difficulty"]}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(f"👥 Serves {recipe['servings']}")
                if st.button("View Recipe", key=f"explore_{recipe['id']}"):
                    st.session_state.selected_recipe_id = recipe["id"]
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif page == "🎲 Surprise Me":
    st.markdown('<div class="section-title">Surprise Me! 🎲</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Let Snap-Bite pick something delicious.</div>', unsafe_allow_html=True)
    if st.button("✨ Pick a Random Recipe", use_container_width=True):
        st.session_state.selected_recipe_id = random.choice(recipes)["id"]
    if st.session_state.selected_recipe_id:
        recipe = next((r for r in recipes if r["id"] == st.session_state.selected_recipe_id), None)
        if recipe:
            render_recipe_detail(recipe)

elif page == "💚 Our Story + Dashboard":
    st.markdown('<div class="section-title">Our Story ❤️</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="story-box">
        <h2 style="color:#054023; margin-top:0;">At Snap-Bite, we believe that great meals can start with what you already have.</h2>
        <p style="color:#61766A;font-size:1.05rem;line-height:1.7;">
        Sometimes, all it takes is a little creativity to turn a few ingredients into something delicious.
        Snap-Bite was created to make cooking easier, smarter, and more inspiring — helping you discover recipes,
        explore new flavors, and make the most of what’s in your kitchen.
        </p>
        <p style="color:#054023;font-size:1.08rem;font-weight:700;">Because every fridge has a story, and every ingredient has a possibility.</p>
        <p style="color:#1E6D4A;font-size:1.15rem;font-weight:800;">Snap it. Cook it. Enjoy it. 🍴✨</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Snap-Bite Insights 📊")
    avg_cal = round(sum(r["calories"] for r in recipes) / len(recipes)) if recipes else 0
    avg_time = round(sum(r["time"] for r in recipes) / len(recipes)) if recipes else 0
    metrics = [
        (len(recipes), "Recipes"),
        (len(set(r["category"] for r in recipes)), "Categories"),
        (len(set(r["cuisine"] for r in recipes)), "Cuisines"),
        (avg_cal, "Avg. Calories / Serving"),
        (avg_time, "Avg. Time (min)"),
    ]
    mcols = st.columns(5)
    for col, (num, label) in zip(mcols, metrics):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-num">{num}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Recipes by Category")
        category_counts = pd.Series([r["category"] for r in recipes]).value_counts().sort_values(ascending=False)
        st.bar_chart(category_counts)
    with c2:
        st.markdown("### Recipes by Cuisine")
        cuisine_counts = pd.Series([r["cuisine"] for r in recipes]).value_counts().sort_values(ascending=False)
        st.bar_chart(cuisine_counts)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("### Difficulty Distribution")
        diff_counts = pd.Series([r["difficulty"] for r in recipes]).value_counts().sort_values(ascending=False)
        st.bar_chart(diff_counts)
    with c4:
        st.markdown("### Meal Timing")
        time_bins = pd.cut([r["time"] for r in recipes], bins=[-1,15,30,60,999], labels=["≤15 min","16–30 min","31–60 min","60+ min"])
        st.bar_chart(pd.Series(time_bins).value_counts().reindex(["≤15 min","16–30 min","31–60 min","60+ min"]).fillna(0))

