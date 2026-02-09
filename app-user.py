import streamlit as st
import json
import os
from datetime import datetime, date
from agents.NexaChatBot import ChatNexa
from agents.user_data_loger import user_data_loger
from agents.calorie_logger import get_macronutrient_breakdown
from agents.workout_logger import get_workout_details
from tools.database_utils import text_to_db
st.set_page_config(page_title="NEXA Fitness App", page_icon="💪", layout="centered")

USERS_FILE = "config/users.json"
 

# -------------------- Helpers --------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)
    user_data_loger(users.get(st.session_state.user_name,{}),st.session_state.user_name)
    print(f"User data for {st.session_state.user_name} saved.")

    


def go_to(page: str):
    st.session_state.page = page


# -------------------- Session Defaults --------------------
if "page" not in st.session_state:
    st.session_state.page = "signin"

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hi {st.session_state.user_name} ✅ Ask me anything!"}
    ]


# -------------------- Pages --------------------
def signin_page():
    st.title("🔐 Sign In")
    st.write("Enter your username to continue.")

    user_name = "user_" + st.text_input("Username", placeholder="e.g. pranay_satija")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Continue ✅", use_container_width=True):
            if not user_name.strip():
                st.error("Username cannot be empty.")
                return

            users = load_users()

            # Existing user → dashboard
            if user_name in users:
                st.session_state.user_name = user_name
                go_to("dashboard")
                st.rerun()
            else:
                # New user → registration
                st.session_state.user_name = user_name
                go_to("register")
                st.rerun()

    with col2:
        if st.button("Reset", use_container_width=True):
            st.session_state.user_name = None
            go_to("signin")
            st.rerun()

 

def register_page():
    st.title("📝 New User Registration")
    st.write(f"Creating profile for: **{st.session_state.user_name}**")

    with st.form("register_form"):
        full_name = st.text_input("Full Name", placeholder="e.g. Pranay Satija")
        age = st.number_input("Age", min_value=1, max_value=120, value=18, step=1)
        height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.5)
        weight_kg = st.number_input("Weight (kg)", min_value=10.0, max_value=400.0, value=70.0, step=0.5)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        goals= st.text_area("Fitness Goals", placeholder="e.g. Build muscle, lose fat, improve endurance")
        coach_id= st.text_input("Coach ID (if any)", placeholder="e.g. coach_123")

        submitted = st.form_submit_button("Create Account ✅", use_container_width=True)

        if submitted:
            users = load_users()

            users[st.session_state.user_name] = {
                "full_name": full_name,
                "age": int(age),
                "height_cm": float(height_cm),
                "weight_kg": float(weight_kg),
                "gender": gender,
                "goals": goals,
                "coach_id": coach_id,
                "created_at": datetime.now().isoformat()
            }

            save_users(users)

            st.success("✅ Account created successfully!")
            go_to("dashboard")

            # reset chat history on first signup
            st.session_state.messages = [
                {"role": "assistant", "content": f"Hi {st.session_state.user_name} ✅ Ask me anything!"}
            ]

            st.rerun()

    if st.button("⬅️ Back to Sign In", use_container_width=True):
        st.session_state.user_name = None
        go_to("signin")
        st.rerun()


# -------------------- NEXA Chat UI --------------------
def chatbot_reply(user_text: str, user_name: str) -> str:
    input_state = {
        "query": user_text,
        "user_name": user_name
    }
    output_text = ChatNexa.invoke(input_state)
    print(output_text)
    return output_text.get("final_output", "Sorry, I could not process your request at the moment.")


def chat_ui(user_name: str):
    st.subheader("🤖 NEXA AI ChatBot")

    # Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("Type your message...")

    if user_input:
        # store user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # generate assistant response
        reply = chatbot_reply(user_input, user_name)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

#----------------------------------------------------------
# -------------------- Food Logging UI --------------------
#----------------------------------------------------------

def log_food_ui(user_name: str):
    
    st.subheader("🍎 Log Your Food Intake")
    print(st.session_state.user_name)
    if not os.path.exists(f"config/{st.session_state.user_name}/food"): 
        os.makedirs(f"config/{st.session_state.user_name}/food")
    if not os.path.exists(f"config/{st.session_state.user_name}/food/{date.today().isoformat()}.json"): 
        with open(f"config/{st.session_state.user_name}/food/{date.today().isoformat()}.json", "w", encoding="utf-8") as f:
            json.dump({}, f) 
    with open(f"config/{st.session_state.user_name}/food/{date.today().isoformat()}.json", "r", encoding="utf-8") as f:
        food = json.load(f)
    with st.form("meal_entry_form"):
        meal_type = st.selectbox(
        "Select the meal type",
        ["breakfast","lunch","dinner","snacks"]
        )
        col1, col2 = st.columns(2)
        with col1:
            food_item = st.text_input("Food Item", placeholder="e.g. Boiled Eggs")
        with col2:
            quantity = st.number_input("Quantity (grams)", min_value=1.0, max_value=10000.0, value=100.0, step=1.0)
        submitted = st.form_submit_button("log food ✅", use_container_width=True)
        if submitted:
            food_item_details=get_macronutrient_breakdown(food_item, quantity)
            print(food_item_details)
            if not food.get(meal_type):
                food[meal_type]=[]
            food[meal_type].append(food_item_details)
            text_to_db(str(food_item_details),database_name="user_dataDB",user_name=st.session_state.user_name,coach_id=load_users().get(st.session_state.user_name,{}).get("coach_id","default"))
            with open(f"config/{st.session_state.user_name}/food/{date.today().isoformat()}.json", "w", encoding="utf-8") as f:
                json.dump(food, f)
    count=0
    for meal, items in food.items():
        for item in items:
            count+=float(item['macronutrients']['calories'])
            
    st.markdown(f"### 🔥 Total Calories Consumed Today: {count:.2f} kcal")
    st.json(food)

#----------------------------------------------------------
# -------------------- Workout Logging UI --------------------
#----------------------------------------------------------

def log_workout_ui(user_name: str):
    
    st.subheader("💪 Log Your Workout")
    print(st.session_state.user_name)
    if not os.path.exists(f"config/{st.session_state.user_name}/workout"): 
        os.makedirs(f"config/{st.session_state.user_name}/workout")
    if not os.path.exists(f"config/{st.session_state.user_name}/workout/{date.today().isoformat()}.json"): 
        with open(f"config/{st.session_state.user_name}/workout/{date.today().isoformat()}.json", "w", encoding="utf-8") as f:
            json.dump({}, f) 
    with open(f"config/{st.session_state.user_name}/workout/{date.today().isoformat()}.json", "r", encoding="utf-8") as f:
        workout = json.load(f)
    with st.form("workout_entry_form"):
        meal_type = st.selectbox(
        "Select the workout type",
        ["morning","afternoon","evening","night"]
        )
        col1, col2 = st.columns(2)
        with col1:
            workout_item = st.text_input("Workout Item", placeholder="e.g. Running")
        with col2:
            quantity = st.number_input("minutes", min_value=1.0, max_value=1000.0, value=45.0, step=5.0)
        submitted = st.form_submit_button("log workout ✅", use_container_width=True)
        if submitted:
            workout_details=get_workout_details(workout_item, quantity)
            print(workout_details)
            if not workout.get(meal_type):
                workout[meal_type]=[]
            workout[meal_type].append(workout_details)
            text_to_db(str(workout_details),database_name="user_dataDB",user_name=st.session_state.user_name,coach_id=load_users().get(st.session_state.user_name,{}).get("coach_id","default"))
            with open(f"config/{st.session_state.user_name}/workout/{date.today().isoformat()}.json", "w", encoding="utf-8") as f:
                json.dump(workout, f)
    count=0
    for meal, items in workout.items():
        for item in items:
            count+=float(item['workout_details']['calories_burned'])

    st.markdown(f"### 🔥 Total Calories Burned Today: {count:.2f} kcal")
    st.json(workout)


    
def dashboard_page():
    users = load_users()

    if not st.session_state.user_name:
        go_to("signin")
        st.rerun()

    user_name = st.session_state.user_name
    user_data = users.get(user_name)

    if user_data is None:
        st.warning("User profile not found. Please register again.")
        go_to("register")
        st.rerun()

    st.title("🏠 Dashboard")
    st.write(f"Welcome **{user_name}** ✅")

    with st.expander("📌 View Profile"):
        st.json(user_data)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": f"Hi{st.session_state.user_name} ✅ Ask me anything!"}
            ]
            st.rerun()

    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_name = None
            go_to("signin")
            st.rerun()

    with col3:
        if st.button("🗑️ Delete Account", use_container_width=True):
            users = load_users()
            if user_name in users:
                del users[user_name]
                save_users(users)

            st.session_state.user_name = None
            st.session_state.messages = [
                {"role": "assistant", "content": f"Hi {st.session_state.user_name} ✅ Ask me anything!"}
            ]
            go_to("signin")
            st.rerun()

    st.divider()

    log_food_ui(user_name)

    st.divider()
    log_workout_ui(user_name)
    st.divider()
    # ✅ Chatbot inside Dashboard
    chat_ui(user_name)




# -------------------- Router --------------------
if st.session_state.page == "signin":
    signin_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "dashboard":
    dashboard_page()
else:
    go_to("signin")
    st.rerun()