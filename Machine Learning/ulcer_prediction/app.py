import streamlit as st
import pandas as pd
import numpy as np
import pickle


# -----------------------------
# Load model and scaler
# -----------------------------
with open("best_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# -----------------------------
# App Title
# -----------------------------
st.set_page_config(page_title="Ulcer Risk Prediction", layout="wide")
st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(
        135deg,
        #020617 0%,
        #0f172a 35%,
        #0b2447 70%,
        #0a192f 100%
    );
}

/* Main container */
.block-container {
    max-width: 95% !important;
    padding-top: 2rem;
}

/* Title */
h1 {
    color: white !important;
    text-align: center;
    font-weight: 700;
}

/* Subtitle */
p {
    color: #cbd5e1;
}

/* Input cards */
[data-testid="column"] {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 18px;
    padding: 20px;
    backdrop-filter: blur(12px);
    box-shadow:
        0 0 20px rgba(59,130,246,0.15),
        0 0 40px rgba(59,130,246,0.08);
}

/* Labels */
label {
    color: #e2e8f0 !important;
    font-weight: 600;
}

/* Input boxes */
.stSelectbox div,
.stNumberInput div,
.stSlider {
    border-radius: 12px !important;
}

/* Predict button */
.stButton > button {
    width: 100%;
    height: 55px;
    border-radius: 14px;
    border: none;
    color: white;
    font-size: 18px;
    font-weight: bold;

    background: linear-gradient(
        90deg,
        #2563eb,
        #3b82f6,
        #60a5fa
    );

    box-shadow:
        0 0 15px rgba(59,130,246,0.6),
        0 0 30px rgba(59,130,246,0.3);

    transition: all 0.3s ease;
}

/* Hover effect */
.stButton > button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 0 25px rgba(59,130,246,0.9),
        0 0 50px rgba(59,130,246,0.5);
}

/* Success box */
.stSuccess {
    border-radius: 12px;
}

/* Error box */
.stError {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

st.title("🩺 Ulcer Risk Prediction App")
st.write("Enter patient details to predict ulcer risk")

# -----------------------------
# User Inputs
# -----------------------------
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 👤 Personal Information")
    Age = st.slider("Age", 18, 90, 40)
    Gender = st.selectbox("Gender", ["Male", "Female"])
    Height_cm = st.number_input("Height (cm)", 140.0, 200.0, 170.0)
    Weight_kg = st.number_input("Weight (kg)", 35.0, 150.0, 70.0)

    Smoking = st.selectbox("Smoking", ["Yes", "No"])
    Alcohol_Use = st.selectbox("Alcohol Use", ["Yes", "No"])
    NSAID_Use = st.selectbox("NSAID Use", ["Yes", "No"],help="Use of pain-relief medicines such as Ibuprofen, Diclofenac, Aspirin, or Naproxen.")

    Family_History = st.selectbox("Family History", ["Yes", "No"], help="Whether a close family member has had ulcers or similar digestive conditions.")
    Stress_Level = st.slider("Stress Level (1–10)", 1, 10, 5)

with col2:
    st.markdown("### 🩺 Symptoms Check")
    
    Abdominal_Pain = st.selectbox( "Abdominal Pain (Stomach Pain)", ["Yes", "No"], help="Pain or discomfort in the stomach or belly area.")
    Nausea = st.selectbox("Nausea", ["Yes", "No"],  help="Feeling sick to your stomach or feeling like you may vomit.")
    Vomiting = st.selectbox("Vomiting", ["Yes", "No"], help="Forcefully throwing up stomach contents.")
    Bloating = st.selectbox("Bloating", ["Yes", "No"], help="Feeling of fullness, tightness, or swelling in the abdomen.")
    Loss_of_Appetite = st.selectbox("Loss of Appetite", ["Yes", "No"], help="Reduced desire to eat food")
    Heartburn = st.selectbox("Heartburn", ["Yes", "No"], help="Burning sensation in the chest or throat caused by acid reflux.")
    Melena = st.selectbox("Melena (Black Stools)", ["Yes", "No"], help="Have your stools (poop) appeared black, tarry stools that may indicate bleeding in the digestive tract.")
    Hematemesis = st.selectbox("Hematemesis (Vomiting Blood)", ["Yes", "No"], help="Vomiting blood or material that looks like coffee grounds.")

# -----------------------------
# Encode categorical values
# -----------------------------
def encode(val):
    return 1 if val == "Yes" else 0

input_data = pd.DataFrame([{
    "Age": Age,
    "Gender": 1 if Gender == "Male" else 0,
    "Height_cm": Height_cm,
    "Weight_kg": Weight_kg,
    "Smoking": encode(Smoking),
    "Alcohol_Use": encode(Alcohol_Use),
    "NSAID_Use": encode(NSAID_Use),
    "Stress_Level": Stress_Level,
    "Family_History": encode(Family_History),
    "Abdominal_Pain": encode(Abdominal_Pain),
    "Nausea": encode(Nausea),
    "Vomiting": encode(Vomiting),
    "Bloating": encode(Bloating),
    "Loss_of_Appetite": encode(Loss_of_Appetite),
    "Heartburn": encode(Heartburn),
    "Melena": encode(Melena),
    "Hematemesis": encode(Hematemesis)
}])

# -----------------------------
# Prediction
# -----------------------------
if st.button("🔍 Predict Ulcer Risk"):

    # Columns used during scaler training
    scale_cols = ['Age', 'Height_cm', 'Weight_kg', 'Stress_Level']

    # Scale only those columns
    input_data_scaled = input_data.copy()

    input_data_scaled[scale_cols] = scaler.transform(
        input_data[scale_cols]
    )

    # Predict
    risk_score = model.predict(input_data_scaled)[0]

    st.subheader("🧾 Prediction Result")
    st.write(f"**Ulcer Risk Score:** `{risk_score:.2f}`")

    # -----------------------------
    # Risk Interpretation Logic
    # -----------------------------
    if risk_score <= 0.3:
        st.success("🟢 No Ulcer Risk Detected")
        st.info("Your risk is low. Maintain a healthy lifestyle with balanced diet, proper sleep, and regular exercise.")

    elif 0.3 < risk_score <= 0.5:
        st.warning("🟡 Low to Moderate Risk (Future Risk Possible)")
        st.info(
            "You currently show mild risk signs. "
            "There is no immediate ulcer indication, but you should take care of your health.\n\n"
            "✔ Eat healthy food\n"
            "✔ Avoid spicy/oily food\n"
            "✔ Sleep well (7–8 hours)\n"
            "✔ Practice yoga or meditation\n"
            "✔ Exercise regularly"
        )

    else:
        st.error("🔴 High Risk of Ulcer Detected")
        st.warning(
            "Your symptoms indicate a higher probability of ulcer. "
            "It is strongly recommended to consult a doctor or gastroenterologist for proper diagnosis."
        )