import streamlit as st
import os
import json

from user import (
    register_user,
    login_user,
    is_admin,
    get_user_id,
    get_all_users,
    delete_user,
    create_default_admin,
    any_admin_exists
)
from database import (
    save_prediction, 
    get_user_predictions, 
    get_all_predictions, 
    delete_predictions_by_user, 
    delete_prediction_at_index,
    save_chat_message, 
    get_user_chats, 
    get_all_chats, 
    delete_chats_by_user, 
    delete_chat_at_index
)


from PIL import Image
import tensorflow as tf
import numpy as np
import cv2
import random
from googletrans import Translator
# after your imports in app.py
from user import create_default_admin, any_admin_exists


# create a default admin if none exists (only on first run)
if not any_admin_exists():
    # change password right after first login for safety
    created = create_default_admin(username="admin", password="admin123")
    if created:
        print("Default admin created: username='admin' password='admin123' — change immediately.")



model_path = "CNN_plant_disease_model.keras"


if os.path.exists(model_path):
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"Model loaded successfully from {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        exit()
else:
    print(f"Model file not found: {model_path}")
    exit()


lang_dict = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Odia": "or",
    "Assamese": "as",
    "Urdu": "ur"
}



translator = Translator()

PLANT_DISEASES_FILE = "plant_diseases.json" 

def get_plantdoctor_response(user_input, lang_code="en"):
    # Load the plant diseases dataset
    with open(PLANT_DISEASES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    responses = []
    
    for disease in data["plant_diseases"]:
        for keyword in disease["keywords"]:
            if keyword.lower() in user_input.lower():
                response_text = (
                    f"Disease: {disease['class']}\n"
                    f"Symptoms: {', '.join(disease['symptoms'])}\n"
                    f"Solutions: {', '.join(disease['solutions'])}"
                )
                if lang_code != "en":
                    response_text = translator.translate(response_text, dest=lang_code).text
                responses.append(response_text)
    
    if responses:
        return random.choice(responses)
    else:
        default_msg = "Sorry, I couldn't identify the plant disease. Please try again or upload an image."
        if lang_code != "en":
            default_msg = translator.translate(default_msg, dest=lang_code).text
        return default_msg



if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


st.sidebar.title("🌱 Plant Disease Detection")
selected_lang = st.sidebar.selectbox("Choose Language", list(lang_dict.keys()))
lang_code = lang_dict[selected_lang]

if st.session_state["logged_in"]:
    st.sidebar.success(f"Hello, {st.session_state['username']} 👋")
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

if st.session_state.get("logged_in"):
    if is_admin(st.session_state["username"]):
      menu = st.sidebar.radio("Menu", ["Disease Recognition", "My History", "My Chats", "Admin Dashboard"])
    else:
        menu = st.sidebar.radio("Menu", ["Disease Recognition", "My History", "My Chats"])
else:
    menu = st.sidebar.radio("Menu", ["Login", "Sign Up"])



if menu == "Sign Up":
    st.subheader("Create a New Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if register_user(new_user, new_pass):
            st.success("✅ Account created successfully! Please log in.")
        else:
            st.error("❌ Username already exists. Try another one.")


elif menu == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

elif menu == "Disease Recognition":
    if not st.session_state["logged_in"]:
        st.warning("⚠️ You need to log in first.")
    else:
        st.header(translator.translate("Disease Recognition: Detect and Ask", dest=lang_code).text)

        # ====== Image Upload & Prediction ======
        uploaded_file = st.file_uploader(translator.translate("Upload an image to detect plant diseases:", dest=lang_code).text,
                                         type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, caption=translator.translate("Uploaded Image", dest=lang_code).text,
                     use_container_width=True)
            save_path = os.path.join(os.getcwd(), uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Class names and advisory messages
                class_name = [ 'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy' ] # Add your class names here 
                advisory_messages = { 'Apple___Apple_scab': "Apple scab can be controlled by applying fungicides. Prune affected areas and avoid overhead watering.", 'Apple___Black_rot': "Black rot can be treated by removing infected fruits and branches. Fungicides can also help.", 'Apple___Cedar_apple_rust': "Cedar apple rust can be managed by removing affected leaves and applying fungicides.", # More diseases here... 
                                     'Tomato___healthy': "Your tomato plant is healthy!", 'Apple___Apple_scab': "Apply fungicide sprays (e.g., Captan, Mancozeb) and remove infected leaves.", 'Apple___Black_rot': "Prune infected branches, remove mummified fruit, and apply copper-based fungicides.", 'Apple___Cedar_apple_rust': "Use resistant apple varieties and apply fungicide sprays at bud break.", 'Apple___healthy': "No treatment needed. Maintain proper orchard hygiene.", 'Blueberry___healthy': "Your plant is healthy! Maintain soil moisture and monitor for pests.", 'Cherry_(including_sour)___Powdery_mildew': "Apply sulfur-based or neem oil sprays and prune overcrowded branches.", 'Cherry_(including_sour)___healthy': "No treatment required. Ensure proper watering and pruning.", 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': "Use resistant varieties, rotate crops, and apply fungicides like azoxystrobin.", 'Corn_(maize)___Common_rust_': "Plant resistant hybrids and apply fungicides if necessary.", 'Corn_(maize)___Northern_Leaf_Blight': "Remove infected debris, use fungicides like propiconazole, and practice crop rotation.", 'Corn_(maize)___healthy': "Your corn is healthy! Maintain proper irrigation and nutrient balance.", 'Grape___Black_rot': "Remove infected leaves and fruits, ensure good air circulation, and apply fungicides like myclobutanil.", 'Grape___Esca_(Black_Measles)': "Prune infected vines, avoid overwatering, and apply fungicides like flutriafol.", 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': "Use copper fungicides and ensure proper vineyard spacing for airflow.", 'Grape___healthy': "No issues detected. Keep monitoring for signs of disease.", 'Orange___Haunglongbing_(Citrus_greening)': "Control psyllid insects with insecticides and remove infected trees if necessary.", 'Peach___Bacterial_spot': "Apply copper sprays before bud break and avoid overhead irrigation.", 'Peach___healthy': "No issues detected. Keep monitoring for pests and diseases.", 'Pepper,_bell___Bacterial_spot': "Apply copper fungicides and practice crop rotation.", 'Pepper,_bell___healthy': "No treatment needed. Maintain optimal soil moisture and nutrients.", 'Potato___Early_blight': "Use fungicides like chlorothalonil and remove infected leaves.", 'Potato___Late_blight': "Apply fungicides like metalaxyl and avoid excessive moisture.", 'Potato___healthy': "Your potato plants are healthy! Keep monitoring for any signs of disease.", 'Raspberry___healthy': "No issues detected. Ensure proper pruning for airflow.", 'Soybean___healthy': "No disease detected. Maintain proper soil health and irrigation.", 'Squash___Powdery_mildew': "Use sulfur-based fungicides and avoid overhead watering.", 'Strawberry___Leaf_scorch': "Remove infected leaves and apply fungicides like Captan.", 'Strawberry___healthy': "Your strawberry plants are healthy! Keep monitoring for pests.", 'Tomato___Bacterial_spot': "Apply copper sprays and avoid overhead watering.", 'Tomato___Early_blight': "Rotate crops, remove infected leaves, and use fungicides like chlorothalonil.", 'Tomato___Late_blight': "Apply copper-based fungicides and remove affected leaves.", 'Tomato___Leaf_Mold': "Improve air circulation, remove affected leaves, and apply fungicides.", 'Tomato___Septoria_leaf_spot': "Use fungicides like chlorothalonil and practice crop rotation.", 'Tomato___Spider_mites Two-spotted_spider_mite': "Use neem oil or insecticidal soap to control mites.", 'Tomato___Target_Spot': "Apply fungicides and remove infected leaves.", 'Tomato___Tomato_Yellow_Leaf_Curl_Virus': "Use virus-resistant seeds and control whiteflies.", 'Tomato___Tomato_mosaic_virus': "Remove infected plants and disinfect gardening tools.", 'Tomato___healthy': "Your tomato plant is healthy! Maintain good watering and fertilization practices." } # Add your advisory messages here 
                product_links = { 'Apple___Apple_scab': [ {"name": "Captan Fungicide", "url": "https://example.com/captan-fungicide"}, {"name": "Mancozeb Fungicide", "url": "https://example.com/mancozeb-fungicide"} ], 'Apple___Black_rot': [ {"name": "Copper Fungicide", "url": "https://example.com/copper-fungicide"}, {"name": "Pruning Shears", "url": "https://example.com/pruning-shears"} ], 'Apple___Cedar_apple_rust': [ {"name": "Captan Fungicide", "url": "https://www.westonnurseries.com/cedar-apple-rust/?utm_source=chatgpt.com"}, {"name": "Mancozeb Fungicide", "url": "https://kb.jniplants.com/preventing-cedar-apple-rust?utm_source=chatgpt.com"} ], 'Potato___Early_blight': [ {"name": "Copper Fungicide", "url": "https://krushidukan.bharatagri.com/en/products/potato-surkasha-kit-blight-1?variant=43452570599667&currency=INR&utm_source=google&utm_medium=organic&utm_campaign=Primary%20Feed%20English&utm_content=%E0%A4%86%E0%A4%B2%E0%A5%82%20%E0%A4%B8%E0%A5%81%E0%A4%B0%E0%A4%95%E0%A5%8D%E0%A4%B7%E0%A4%BE%20%E0%A4%95%E0%A4%BF%E0%A4%9F%20-%20%E0%A4%9D%E0%A5%81%E0%A4%B2%E0%A4%B8%E0%A4%BE%20%E0%A4%B0%E0%A5%8B%E0%A4%97%20%E0%A4%A8%E0%A4%BF%E0%A4%AF%E0%A4%82%E0%A4%A4%E0%A5%8D%E0%A4%B0%E0%A4%A3%20(25-90%20%E0%A4%A6%E0%A4%BF%E0%A4%A8)&srsltid=AfmBOopLVmRNEevNO_jBnzRE9KkhXElR9T576tqebQyYMn5HYl5_-3BxvhY"}, {"name": "Pruning Shears", "url": "https://krushidukan.bharatagri.com/en/products/control-kit-in-turmeric-ginger?variant=45881589137651&country=IN&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&srsltid=AfmBOopUbV3Fm1-fEEipAsFVihQdSEioQDBpv1Hq7nrV9cdCeX9NZf7Ae1Y"} ],
                            
                                }

            # Prediction function
            def model_predict(image_path):
                img = cv2.imread(image_path)
                img = cv2.resize(img, (224, 224))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = np.array(img).astype("float32") / 255.0
                img = img.reshape(1, 224, 224, 3)
                prediction = np.argmax(model.predict(img), axis=-1)[0]
                return prediction

            # Predict button
            if st.button(translator.translate("Predict", dest=lang_code).text):
                result_index = model_predict(save_path)
                if result_index < len(class_name):
                    predicted_disease = class_name[result_index]

                    # Save history
                    user_id = get_user_id(st.session_state["username"])
                    if user_id:
                        save_prediction(user_id, predicted_disease)

                    # Display prediction
                    translated_disease = translator.translate(predicted_disease, dest=lang_code).text
                    st.success(translator.translate("Model predicts:", dest=lang_code).text + " " + translated_disease)

                    # Advisory message
                    if predicted_disease in advisory_messages:
                        translated_advice = translator.translate(advisory_messages[predicted_disease], dest=lang_code).text
                        st.subheader(translator.translate("Advisory:", dest=lang_code).text)
                        st.write(translated_advice)

                    # Product links
                    if predicted_disease in product_links:
                        st.subheader(translator.translate("Recommended Products:", dest=lang_code).text)
                        for product in product_links[predicted_disease]:
                            st.markdown(f"[{product['name']}]({product['url']})")

                else:
                    st.error("Prediction index out of range. Check class list.")

       # ====== PlantDoctor Chat Section ======
        st.subheader(translator.translate("💬 Ask PlantDoctor", dest=lang_code).text)

        # Q&A Knowledge Base
        qa_pairs = {
            "greeting": "Hello! 👋 I’m your PlantDoctor 🌿. How can I help your plants today?",
    "thanks": "You're welcome! 😊 Keep your plants happy and healthy 🌻",
    "who are you": "I'm PlantDoctor, your AI gardening buddy! I help diagnose plant problems and share care tips.",

    # Common issues
    "yellow leaves": "🌿 Yellow leaves usually mean overwatering or lack of nitrogen. Let the soil dry before watering and add a balanced fertilizer.",
    "brown spots": "🍂 Brown spots often indicate fungal infection. Remove infected leaves and apply a mild fungicide like neem oil.",
    "wilting": "😞 Wilting might be from underwatering, heat stress, or root rot. Check soil moisture and avoid waterlogging.",
    "white powder": "🌫️ White powder on leaves is powdery mildew. Increase air circulation and spray neem oil or baking soda solution.",
    "leaf curling": "🌀 Leaf curling can occur due to pest attacks, over-fertilizing, or temperature stress.",
    "dropping leaves": "🍃 Leaf drop can be caused by sudden temperature changes or lack of light. Keep the plant in a stable environment.",
    "holes in leaves": "🐛 Holes usually mean pest activity like caterpillars or beetles. Inspect and remove pests manually or use neem spray.",
    "sticky leaves": "🌸 Sticky leaves could mean aphids or mealybugs. Wipe them with soapy water and spray neem oil.",
    "black spots": "⚫ Black spots on leaves may be a fungal disease. Remove affected parts and keep leaves dry.",
    "brown tips": "🌾 Brown leaf tips often mean low humidity or too much fertilizer. Mist your plants or flush the soil with water.",

    # Growth & care
    "fertilizer": "🧪 Use nitrogen-rich fertilizer for leafy plants and phosphorus-rich for flowering plants.",
    "watering": "💧 Water when the top 2 inches of soil are dry. Avoid letting the plant sit in water.",
    "sunlight": "☀️ Most indoor plants prefer indirect sunlight. Too much direct sun can scorch the leaves.",
    "repotting": "🪴 Repot every 6–12 months or when roots start peeking through the bottom holes.",
    "pruning": "✂️ Regular pruning helps plants grow fuller and removes dead parts.",
    "temperature": "🌤️ Most houseplants thrive between 18–28°C. Avoid cold drafts or sudden changes.",
    "humidity": "💦 Many tropical plants love humidity. Mist leaves or use a humidifier if air is dry.",
    "soil": "🌱 Use well-draining soil. For succulents, use cactus mix; for flowering plants, use loamy soil.",
    "lighting": "💡 Too little light causes leggy growth. Move your plant near a window with indirect sunlight.",

    # Pests
    "aphids": "🪲 Aphids are tiny green pests that suck sap. Use neem oil or insecticidal soap weekly until gone.",
    "mealybugs": "⚪ Mealybugs look like white cottony spots. Dab them with alcohol and spray neem oil.",
    "spider mites": "🕷️ Spider mites cause yellow specks and fine webbing. Spray water mist daily and use miticide if needed.",
    "fungus gnats": "🪰 Fungus gnats thrive in moist soil. Let soil dry and use sticky traps.",
    "snails": "🐌 Snails and slugs eat leaves. Handpick them and keep soil dry.",

    # Seasonal care
    "winter care": "❄️ In winter, water less and move plants near light. Avoid cold drafts.",
    "summer care": "☀️ In summer, increase watering and mist leaves more often.",
    "rainy season": "🌧️ During rains, avoid overwatering and check for fungal growth.",
    
    # Fun / small talk
    "joke": "😂 Why did the plant go to therapy? It had too many roots in its past!",
    "motivation": "💪 Keep going! Every leaf you save makes your plant proud of you 🌿",
    "love plants": "💚 Plants are pure magic! They bring peace, beauty, and oxygen.",
    "bye": "👋 Goodbye! Keep your plants smiling and come back anytime 🌻"
        }

    # Fuzzy matching response function
    import difflib, random

    def get_response(user_input, lang_code="en"):
        user_input_lower = user_input.lower()

        # 1️⃣ First, check the plant_diseases JSON keywords
        plant_response = get_plantdoctor_response(user_input, lang_code=lang_code)
        if "Sorry, I couldn't identify the plant disease" not in plant_response:
            return plant_response

        # Basic conversation triggers
        if any(word in user_input_lower for word in ["hi", "hello", "hey"]):
            return qa_pairs["greeting"]
        if "thank" in user_input_lower:
            return qa_pairs["thanks"]
        if "who are you" in user_input_lower or "your name" in user_input_lower:
            return qa_pairs["who are you"]
        if "bye" in user_input_lower or "goodbye" in user_input_lower:
            return qa_pairs["bye"]
        if "joke" in user_input_lower:
            return qa_pairs["joke"]
        if "motivate" in user_input_lower or "motivation" in user_input_lower:
            return qa_pairs["motivation"]
        if "love" in user_input_lower and "plant" in user_input_lower:
            return qa_pairs["love plants"]

        # Best match from QA keys
        best_match = difflib.get_close_matches(user_input_lower, qa_pairs.keys(), n=1, cutoff=0.4)
        if best_match:
            return qa_pairs[best_match[0]]
        else:
            unsure_responses = [
                "🤔 Hmm, I’m not sure about that. Can you describe what your plant looks like?",
                "🪴 Could you tell me more details — color, spots, or any insects?",
                "🌿 That’s interesting! Can you mention which plant it is?",
            ]
            return random.choice(unsure_responses)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input_local = st.chat_input(
            translator.translate("Ask PlantDoctor about your plant...", dest=lang_code).text
        )

        # Process only if user entered something
    if user_input_local:
            # Translate user input to English for keyword matching
            user_input_en = translator.translate(user_input_local, src=lang_code, dest="en").text

            # Get bot response in English
            bot_reply_en = get_response(user_input_en, lang_code="en")

            # Translate bot response back to user's language
            bot_reply_local = translator.translate(bot_reply_en, dest=lang_code).text

            # Save chat (session + database)
            st.session_state.chat_history.append(("You", user_input_local))
            st.session_state.chat_history.append(("PlantDoctor", bot_reply_local))

            user_id = get_user_id(st.session_state["username"])
            if user_id:
                save_chat_message(user_id, user_input_local, bot_reply_local)

       
   # Display session chat (only current session, not global)
            if "chat_history" in st.session_state:
              for sender, msg in st.session_state.chat_history:
                if sender == "You":
                    st.chat_message("user").markdown(msg)
                else:
                    st.chat_message("assistant").markdown(msg)


elif menu == "My History":
       if not st.session_state["logged_in"]: 
           st.warning("⚠️ You need to log in first.") 
       else: 
           st.subheader("📜 Your Past Predictions") 
           user_id = get_user_id(st.session_state["username"]) 
           history = get_user_predictions(user_id)
       if history: 
                 for disease, time in history:
                  st.write(f"🕒 {time} → 🌱 {disease}") 
                 else: 
                   st.info("No history available.") 

elif menu == "My Chats":
    if not st.session_state["logged_in"]:
        st.warning("⚠️ You need to log in first.")
    else:
        st.subheader("🗂️ Your Chat History")
        user_id = get_user_id(st.session_state["username"])
        chats = get_user_chats(user_id)

        if chats:
            for i, c in enumerate(chats):
                st.markdown(f"**🗣️ You:** {c['user_message']}  \n**🤖 Bot:** {c['bot_reply']}")
                if st.button("🗑️ Delete", key=f"del_chat_{i}"):
                    delete_chat_at_index(i, user_id)
                    st.success("✅ Chat deleted.")
                    st.experimental_rerun()
        else:
            st.info("No chat history found.")



elif menu == "Admin Dashboard":
    if not st.session_state.get("logged_in") or not is_admin(st.session_state["username"]):
        st.error("❌ You are not authorized to view this page.")
    else:
        st.subheader("🛠️ Admin Dashboard - Users & Predictions")

        # --- ADMIN TOOLS INFO ---
        st.markdown("### 🔐 Admin Tools")
        st.write("Be careful: deleting a user will remove their account and all their prediction history.")

        # --- ALL USERS ---
        st.markdown("#### 👥 All Users")
        from user import get_all_users, delete_user
        from database import delete_predictions_by_user, get_all_predictions, delete_prediction_at_index

        users = get_all_users()
        if users:
            for u in users:
                uid = u["id"]
                uname = u["username"]
                admin_flag = u.get("is_admin", False)

                cols = st.columns([3,1,1])
                cols[0].write(f"**{uname}** (id: {uid})")
                cols[1].write("Admin" if admin_flag else "User")

                # Delete button - prevent deleting self
                if cols[2].button("Delete user", key=f"delete_user_{uname}"):
                    if uname == st.session_state["username"]:
                        st.error("❌ You cannot delete your own admin account while logged in.")
                    else:
                        deleted = delete_user(uname)
                        if deleted:
                            removed = delete_predictions_by_user(uid)
                            st.success(f"User '{uname}' deleted. Removed {removed} prediction(s).")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Failed to delete user.")
        else:
            st.info("No users found.")

        st.markdown("---")

        # --- ALL PREDICTIONS ---
        st.markdown("#### 📜 All Predictions")
        all_preds = get_all_predictions()
        if all_preds:
            for i, p in enumerate(all_preds):
                line = f"{i}. user_id: {p.get('user_id')} → disease: {p.get('disease')}"
                cols = st.columns([6,1])
                cols[0].write(line)
                if cols[1].button("Delete", key=f"delpred_{i}"):
                    if delete_prediction_at_index(i):
                        st.success(f"Deleted prediction #{i}")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Failed to delete prediction.")

            # Clear all predictions option
            if st.button("Clear all predictions"):
                if st.button("Confirm: Clear ALL predictions", key="confirm_clear_all"):
                    with open("predictions.json", "w", encoding="utf-8") as f:
                        json.dump([], f)
                    st.success("✅ All predictions cleared.")
                    st.experimental_rerun()
        else:
            st.info("No predictions available yet.")

            if st.subheader("💬 All User Chats"):
                all_chats = get_all_chats()
                if all_chats:
                    for i, c in enumerate(all_chats):
                        st.markdown(f"👤 User ID: {c['user_id']}  \n🗣️ You: {c['user_message']}  \n🤖 Bot: {c['bot_reply']}")
                        if st.button("Delete Chat", key=f"adm_del_chat_{i}"):
                           delete_chat_at_index(i)
                           st.success("Deleted chat.")
                           st.rerun()
                        else:
                           st.info("No chats available.")
