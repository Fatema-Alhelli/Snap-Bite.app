import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import os


st.set_page_config(
    page_title="Snap-Bite",
    page_icon="🍴"
)


st.title("🍴 Snap-Bite")
st.subheader("Turn your fridge photo into ingredients")


@st.cache_resource
def load_model():

    model = YOLO("yolov8l-worldv2.pt")

    ingredients = [
        "milk",
        "egg",
        "cheese",
        "chicken",
        "beef",
        "fish",
        "tomato",
        "potato",
        "onion",
        "carrot",
        "cucumber",
        "bell pepper",
        "lettuce",
        "apple",
        "banana",
        "orange",
        "bread",
        "butter",
        "yogurt"
    ]

    model.set_classes(ingredients)

    return model


st.write("Choose how you want to add your fridge photo:")


camera_photo = st.camera_input("📷 Take a photo")


uploaded_file = st.file_uploader(
    "📁 Or upload a photo",
    type=["jpg", "jpeg", "png"]
)


if camera_photo is not None:

    image_source = camera_photo

elif uploaded_file is not None:

    image_source = uploaded_file

else:

    image_source = None


if image_source is not None:

    image = Image.open(image_source)

    st.image(
        image,
        caption="Your fridge image",
        use_container_width=True
    )

    model = load_model()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    ) as tmp:

        image.convert("RGB").save(tmp.name)

        image_path = tmp.name


    try:

        results = model(image_path)

        annotated_image = results[0].plot()

        st.subheader("🔍 Detected Ingredients")

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

            st.warning("No ingredients were detected.")


    finally:

        if os.path.exists(image_path):

            os.remove(image_path)


