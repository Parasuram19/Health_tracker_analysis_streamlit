import streamlit as st
import pandas as pd
import datetime
import numpy as np

# Session State Management
def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    default_states = {
        'user_profile': {
            'name': '',
            'age': None,
            'gender': '',
            'height': None,
            'weight': None,
            'medical_conditions': [],
            'allergies': [],
            'dietary_restrictions': []
        },
        'health_parameters': {
            'blood_pressure': None,
            'sugar_level': None,
            'cholesterol': None
        }
    }
    
    for key, value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

# User Profile Page
def user_profile_page():
    st.title("🩺 Personal Health Profile")
    
    # Initialize session state
    initialize_session_state()
    
    # Personal Information
    st.subheader("Personal Details")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['user_profile']['name'] = st.text_input("Full Name", value=st.session_state['user_profile']['name'])
        st.session_state['user_profile']['age'] = st.number_input("Age", min_value=1, max_value=120, value=st.session_state['user_profile']['age'] or 25)
        st.session_state['user_profile']['gender'] = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if st.session_state['user_profile']['gender'] == '' else ["Male", "Female", "Other"].index(st.session_state['user_profile']['gender']))
    
    with col2:
        st.session_state['user_profile']['height'] = st.number_input("Height (cm)", min_value=50, max_value=250, value=st.session_state['user_profile']['height'] or 170)
        st.session_state['user_profile']['weight'] = st.number_input("Weight (kg)", min_value=20, max_value=300, value=st.session_state['user_profile']['weight'] or 70)
    
    # Medical Conditions
    st.subheader("Medical Information")
    medical_options = [
        "Diabetes", "Hypertension", "High Cholesterol", 
        "Heart Disease", "Obesity", "PCOS", "Thyroid Disorder"
    ]
    st.session_state['user_profile']['medical_conditions'] = st.multiselect(
        "Select Current Medical Conditions", 
        medical_options, 
        default=st.session_state['user_profile']['medical_conditions']
    )
    
    # Allergies and Dietary Restrictions
    col3, col4 = st.columns(2)
    with col3:
        st.session_state['user_profile']['allergies'] = st.multiselect(
            "Food Allergies", 
            ["Nuts", "Dairy", "Gluten", "Shellfish", "Eggs"],
            default=st.session_state['user_profile']['allergies']
        )
    
    with col4:
        st.session_state['user_profile']['dietary_restrictions'] = st.multiselect(
            "Dietary Restrictions", 
            ["Vegetarian", "Vegan", "Kosher", "Halal", "Lactose Intolerant"],
            default=st.session_state['user_profile']['dietary_restrictions']
        )
    
    # Health Parameters
    st.subheader("Current Health Parameters")
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.session_state['health_parameters']['blood_pressure'] = st.number_input(
            "Blood Pressure (SYS)", 
            min_value=80, 
            max_value=200, 
            value=st.session_state['health_parameters']['blood_pressure'] or 120
        )
    
    with col6:
        st.session_state['health_parameters']['sugar_level'] = st.number_input(
            "Sugar Level (mg/dL)", 
            min_value=70, 
            max_value=300, 
            value=st.session_state['health_parameters']['sugar_level'] or 100
        )
    
    with col7:
        st.session_state['health_parameters']['cholesterol'] = st.number_input(
            "Cholesterol (mg/dL)", 
            min_value=100, 
            max_value=500, 
            value=st.session_state['health_parameters']['cholesterol'] or 200
        )
    
    # Save Profile Button
    if st.button("Save Profile"):
        st.success("Profile saved successfully!")
        st.balloons()

# Nutrition Tracking Page
def nutrition_tracking_page():
    st.title("🍽️ Nutrition Intake Tracker")
    
    # Check if user profile is set
    if not st.session_state['user_profile']['name']:
        st.warning("Please set up your profile first!")
        return
    
    # Nutritional Tracking Form
    with st.form("nutrition_intake"):
        st.header(f"Food Intake for {st.session_state['user_profile']['name']}")
        
        # Date and Meal Type
        col1, col2 = st.columns(2)
        with col1:
            intake_date = st.date_input("Date of Intake", datetime.date.today())
        with col2:
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        
        # Food Item Details
        st.subheader("Food Items")
        num_foods = st.number_input("Number of Food Items", min_value=1, max_value=10, value=1)
        
        food_entries = []
        for i in range(num_foods):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                food_name = st.text_input(f"Food Item {i+1} Name", key=f"food_name_{i}")
            with cols[1]:
                quantity = st.number_input(f"Quantity", min_value=0.1, step=0.1, key=f"quantity_{i}")
            with cols[2]:
                unit = st.selectbox(f"Unit", ["g", "ml", "piece"], key=f"unit_{i}")
            
            if food_name:
                food_entries.append({
                    "name": food_name, 
                    "quantity": f"{quantity}{unit}"
                })
        
        # Submit Button
        submitted = st.form_submit_button("Record Meal")
    
    # Add Tracking Logic Here (similar to your existing calculate_food_calories function)

def main():
    st.sidebar.title("Nutrition & Health Tracker")
    
    # Page Navigation
    pages = {
        "👤 User Profile": user_profile_page,
        "🍽️ Nutrition Tracking": nutrition_tracking_page
    }
    
    selection = st.sidebar.radio("Navigate", list(pages.keys()))
    
    # Render selected page
    pages[selection]()

if __name__ == "__main__":
    main()