# 🍴 Snap-Bite

### From What You Have to What You Can Make.

**Live App:**

🔗 [Open Snap-Bite](https://snapbite-app-bh.streamlit.app/)

**Video Link:**

🔗 [Open Video](https://youtu.be/pE8nMUTVEYk)

---

## 🌿 About Snap-Bite

**Snap-Bite** is an AI-powered recipe assistant that helps users decide what to cook using the ingredients they already have at home.

Users can **take a photo, upload an image, speak, or type their ingredients**. Snap-Bite identifies or receives the ingredients and matches them with recipes from its recipe database to suggest suitable meals.

> **Make cooking easier, faster, and more inspiring — using what you already have.**

---

## 🎯 Project Goal

Snap-Bite was created to solve a simple everyday problem:

**“I have ingredients at home, but what can I cook?”**

The application helps users:

- Discover recipe ideas from available ingredients.
- Reduce the time spent deciding what to cook.
- Make better use of ingredients already at home.
- Explore a wide range of recipes in one place.
- Find recipes using different input methods.

---

## ✨ Main Features

### 📸 Snap / Upload

Users can choose between:

- 📷 **Camera** — take a photo directly using the device camera.
- 📁 **Upload** — upload an existing image of ingredients.

### 🤖 AI Ingredient Detection

Snap-Bite uses a **YOLO object detection model** to identify food ingredients from uploaded or captured images.

### 🍴 Explore Recipes

After ingredients are detected, users can select **Explore Recipes** to see multiple recipes that match the detected ingredients.

The system compares the detected ingredients with the existing recipe database and ranks suitable recipes.

### 🎤 Voice Input

Users can speak their ingredients instead of typing them.

Snap-Bite uses **Deepgram Speech-to-Text** to convert the user's voice into text.

The recognized ingredients are then matched with the existing recipe database to find suitable recipes.

### 📝 Text Input

Users can also type the ingredients they have.

The application searches the existing recipe database and displays recipes that match the entered ingredients.

### 📚 Recipe Explorer

Users can browse the recipe collection and search for recipes by name or ingredients.

### 🔎 Smart Filters

Filter recipes by:

- Category
- Cuisine
- Calories
- Cooking time
- Difficulty
- Number of servings

### 👥 Servings Calculator

Choose the number of people and ingredient quantities are adjusted automatically.

### 🎲 Surprise Me

Get a random recipe when you do not know what to cook.

### 🔄 Refresh

A refresh button is available across the main interactive pages to allow users to start a new search or input without refreshing the entire application.

### 📊 Our Story + Dashboard

View Snap-Bite's story together with simple insights about the recipe database.

---

## 🍴 Recipe Database

Snap-Bite includes **200 recipes** across different food categories:

- Breakfast
- Main Dishes
- Soups
- Appetizers & Snacks
- Desserts
- Drinks

The recipes also cover multiple cuisines, including Gulf, Arabic, Italian, Mexican, American, Asian, Indian, Mediterranean, and more.

Each recipe can include:

- Ingredients and quantities
- Number of servings
- Calories per serving
- Preparation time
- Cooking time
- Difficulty level
- Step-by-step instructions
- Oven temperature and time when needed
- Serving suggestion
- Recipe image

---

## 🧠 How It Works

### 📸 Image-Based Recipe Search

```text
📸 Camera / Upload
        ↓
🤖 YOLO Object Detection
        ↓
🥕 Detected Ingredients
        ↓
🔎 Match with Recipe Database
        ↓
🍴 Explore Matching Recipes
        ↓
👩🏻‍🍳 Cook & Enjoy
