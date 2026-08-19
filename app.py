import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="Snap-Bite", page_icon="🍴", layout="centered")

st.title("🍴 Snap-Bite")
st.subheader("Turn a fridge photo into ingredients")

@st.cache_resource
def load_model():
    model = YOLO("yolov8l-worldv2.pt")
    ingredients = [
        "milk", "egg", "cheese", "chicken", "beef", "fish",
        "tomato", "potato", "onion", "carrot", "cucumber",
        "bell pepper", "lettuce", "apple", "banana", "orange",
        "bread", "butter", "yogurt"
    ]
    model.set_classes(ingredients)
    return model

uploaded_file = st.file_uploader(
    "Upload a photo of your fridge",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your fridge image", use_container_width=True)

    if st.button("Detect Ingredients"):
        model = load_model()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            image.convert("RGB").save(tmp.name)
            image_path = tmp.name

        try:
            results = model(image_path)
            annotated_image = results[0].plot()

            st.subheader("Detected Ingredients")
            st.image(
                annotated_image[:, :, ::-1],
                caption="Detected ingredients",
                use_container_width=True
            )

            detected_ingredients = []

            for result in results:
                for cls_id in result.boxes.cls.tolist():
                    name = result.names[int(cls_id)]
                    if name not in detected_ingredients:
                        detected_ingredients.append(name)

            if detected_ingredients:
                for ingredient in detected_ingredients:
                    st.write(f"• {ingredient}")
            else:
                st.warning("No target ingredients were detected.")

        finally:
            if os.path.exists(image_path):
                os.remove(image_path)
