import streamlit as st
import sqlite3

# -----------------------------
# PAGE CONFIG + CLEAN UI
# -----------------------------
st.set_page_config(page_title="Student Energy Footprint", layout="centered")

st.markdown("""
<style>
body { background-color: #f8f9fa; }
h1, h2, h3 { color: #2f3e46; }
.card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px solid #dee2e6;
}
.notice {
    background-color: #f1f3f5;
    padding: 12px;
    border-radius: 6px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("Student Energy Footprint Calculator")
st.caption("Local tool for estimating daily CO₂ emissions from lifestyle choices")

# -----------------------------
# STUDENT DETAILS
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Student details")

name = st.text_input("Name")
education = st.selectbox(
    "Current level of study",
    [
        "School (Class 1–10)",
        "School (Class 11–12)",
        "Undergraduate",
        "Postgraduate",
        "PhD",
        "Other"
    ]
)
city = st.text_input("City")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TRANSPORT
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Transport")

transport_type = st.radio(
    "Type of transport used for commute",
    ["Public transport (bus/train)", "Private transport (car/two-wheeler)"]
)
distance = st.slider("Daily commuting distance (km)", 0, 100, 10)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# DIET – DETAILED & MULTI-ITEM
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Diet (meal-wise, multiple items allowed)")

FOOD_CO2 = {
    "Rice / grains": 0.8,
    "Vegetables / pulses": 0.6,
    "Dairy (milk, paneer, curd)": 1.5,
    "Vegan protein (tofu, soy, legumes)": 1.2,
    "Eggs": 1.8,
    "Chicken": 3.2,
    "Fish": 2.5,
    "Red meat (mutton/beef)": 6.0,
    "Processed / fast food": 4.0
}

ORGANIC_REDUCTION = 0.85   # ~15% lower footprint (conceptual)

diet_co2 = 0

def meal_block(meal_name, key):
    global diet_co2
    st.markdown(f"**{meal_name}**")
    eaten = st.radio(f"Did you consume {meal_name.lower()}?", ["No", "Yes"], key=f"{key}_yes")
    if eaten == "Yes":
        items = st.multiselect(
            f"Select food items for {meal_name.lower()}",
            list(FOOD_CO2.keys()),
            key=f"{key}_items"
        )
        organic = st.checkbox(
            "Mostly organic food for this meal",
            key=f"{key}_organic"
        )

        for item in items:
            value = FOOD_CO2[item]
            if organic:
                value *= ORGANIC_REDUCTION
            diet_co2 += value

meal_block("Breakfast", "bf")
meal_block("Lunch", "lunch")
meal_block("Dinner", "dinner")
meal_block("Snacks", "snacks")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# DEVICE USAGE
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Device usage")

laptop = st.slider("Laptop usage (hours/day)", 0, 24, 6)
mobile = st.slider("Mobile usage (hours/day)", 0, 24, 4)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# AI USAGE
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("AI usage")

use_ai = st.radio("Do you use AI tools (e.g., ChatGPT)?", ["No", "Yes"])
ai_hours = 0
if use_ai == "Yes":
    ai_hours = st.slider("AI usage (hours/day)", 0, 10, 1)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CALCULATE
# -----------------------------
if st.button("Calculate carbon footprint"):

    # Transport CO2
    if "Public" in transport_type:
        transport_co2 = distance * 0.05
    else:
        transport_co2 = distance * 0.18

    # Device CO2
    device_co2 = (laptop * 0.05) + (mobile * 0.01)

    # AI CO2
    ai_co2 = ai_hours * 0.02

    total_co2 = transport_co2 + diet_co2 + device_co2 + ai_co2

    # -----------------------------
    # RESULTS
    # -----------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Results")

    st.write(f"Transport emissions: {transport_co2:.2f} kg CO₂/day")
    st.write(f"Food emissions: {diet_co2:.2f} kg CO₂/day")
    st.write(f"Device emissions: {device_co2:.2f} kg CO₂/day")
    st.write(f"AI-related emissions: {ai_co2:.2f} kg CO₂/day")
    st.markdown(f"**Total daily footprint: {total_co2:.2f} kg CO₂**")
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # SUSTAINABILITY BENCHMARKS
    # -----------------------------
    AVERAGE = 8.0
    RECOMMENDED = 5.0

    st.markdown('<div class="notice">', unsafe_allow_html=True)
    st.write(f"Average student footprint: {AVERAGE} kg CO₂/day")
    st.write(f"Recommended sustainable level: {RECOMMENDED} kg CO₂/day")
    st.markdown('</div>', unsafe_allow_html=True)

    if total_co2 > RECOMMENDED:
        st.warning("Your footprint is above sustainable levels. Suggested actions:")
        if "Private" in transport_type:
            st.write("- Prefer public or shared transport.")
        if diet_co2 > 4:
            st.write("- Reduce animal-based and processed food items.")
            st.write("- Increase plant-based or vegan protein sources.")
        if device_co2 > 2:
            st.write("- Reduce screen time and energy use.")
        if ai_hours > 3:
            st.write("- Limit unnecessary AI queries.")
    else:
        st.success("Your footprint is within sustainable limits.")

    # -----------------------------
    # SAVE TO SQLITE
    # -----------------------------
    conn = sqlite3.connect("footprint.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        education TEXT,
        city TEXT,
        transport REAL,
        diet REAL,
        device REAL,
        ai REAL,
        total REAL
    )
    """)

    cursor.execute(
        """
        INSERT INTO records
        (name, education, city, transport, diet, device, ai, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, education, city, transport_co2, diet_co2, device_co2, ai_co2, total_co2)
    )

    conn.commit()
    conn.close()

    st.caption("Data stored locally. Estimates are indicative and for awareness purposes.")
