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

# Food Dataset Management
@st.cache_data
def load_food_dataset(file_path):
    """
    Create food dataset from Excel file
    
    Args:
        file_path (str): Path to the Excel file
    
    Returns:
        pandas.DataFrame: Comprehensive nutrition dataset
    """
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    # Select key nutritional columns
    nutrition_columns = [
        'Main food description', 
        'Energy (kcal)', 
        'Protein (g)', 
        'Carbohydrate (g)', 
        'Sugars, total (g)',
        'Fiber, total dietary (g)', 
        'Total Fat (g)', 
        'Cholesterol (mg)',
        'Sodium (mg)',
        'Calcium (mg)'
    ]
    
    # Filter columns if they exist
    available_columns = [col for col in nutrition_columns if col in df.columns]
    
    # Create the final dataset with selected columns
    nutrition_data = df[available_columns]
    
    return nutrition_data

def find_food_calories(food_name, dataset):
    """
    Fuzzy search for food items in the dataset
    """
    # Convert food name to lowercase for case-insensitive matching
    food_name = food_name.lower()
    
    # Try exact match first
    exact_matches = dataset[dataset['Main food description'].str.lower() == food_name]
    
    # If no exact match, try partial match
    if len(exact_matches) == 0:
        partial_matches = dataset[dataset['Main food description'].str.lower().str.contains(food_name)]
        
        if len(partial_matches) > 0:
            # If multiple partial matches, choose the first one
            match = partial_matches.iloc[0]
        else:
            # If no match found, return default values
            return {
                'calories': 0, 
                'protein': 0, 
                'carbs': 0, 
                'fat': 0,
                'match_type': 'No match found'
            }
    else:
        # Use the first exact match if multiple exist
        match = exact_matches.iloc[0]
    
    # Convert energy from fraction to full 100g calories
    calories_per_100g = match['Energy (kcal)'] * 100
    
    return {
        'calories': calories_per_100g, 
        'protein': match['Protein (g)'] * 100, 
        'carbs': match['Carbohydrate (g)'] * 100, 
        'fat': match['Total Fat (g)'] * 100,
        'match_type': 'Exact' if len(exact_matches) > 0 else 'Partial',
        'food_description': match['Main food description']
    }

def calculate_nutritional_info(food_entries, query_item, dataset):
    """
    Calculate total calories and nutritional information for a specific food item from food entries.

    Args:
        food_entries (list): A list of dictionaries with keys 'name' and 'quantity'.
        query_item (str): The food item to query for.
        dataset (pandas.DataFrame): Dataset containing nutritional information.

    Returns:
        dict: A dictionary with total calories, proteins, carbs, fats, breakdown, and unmatched foods.
    """
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    detailed_breakdown = []
    unmatched_foods = []

    for entry in food_entries:
        food_name = entry['name']
        quantity_str = entry['quantity']

        # Skip entries that do not match the query item
        if query_item.lower() not in food_name.lower():
            continue

        # Determine quantity and unit
        try:
            quantity = float(''.join(filter(str.isdigit, quantity_str)))
            unit = ''.join(filter(str.isalpha, quantity_str)).lower()
        except:
            print(f"Could not process quantity for {food_name}")
            unmatched_foods.append(food_name)
            continue

        # Conversion factors
        unit_multipliers = {
            'g': 1,
            'ml': 1,
            'piece': 100
        }

        # Get multiplier, default to 1 if unit not recognized
        multiplier = quantity / 100 * unit_multipliers.get(unit, 1)

        # Get calorie information
        food_info = find_food_calories(food_name, dataset)

        if food_info['match_type'] == 'No match found':
            unmatched_foods.append(food_name)
            continue

        # Calculate nutritional values
        calories = food_info['calories'] * multiplier
        protein = food_info['protein'] * multiplier
        carbs = food_info['carbs'] * multiplier
        fat = food_info['fat'] * multiplier

        total_calories += calories
        total_protein += protein
        total_carbs += carbs
        total_fat += fat

        # Create detailed breakdown entry
        breakdown_entry = f"{food_info['food_description']} ({quantity_str}): {calories:.0f} cal (Protein: {protein:.1f}g, Carbs: {carbs:.1f}g, Fat: {fat:.1f}g)"
        detailed_breakdown.append(breakdown_entry)

    return {
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat,
        'breakdown': "\n".join(detailed_breakdown),
        'unmatched_foods': unmatched_foods
    }


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

def nutrition_tracking_page():
    st.title("🍽️ Nutrition Intake Tracker")
    file_path = '2017-2018 FNDDS At A Glance - FNDDS Nutrient Values.xlsx'
    # Load food dataset
    food_dataset = load_food_dataset(file_path)
    
    # Check if user profile is set
    if 'user_profile' not in st.session_state or not st.session_state['user_profile']['name']:
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
                quantity = st.text_input(f"Quantity (e.g. 200g)", key=f"quantity_{i}")
            
            if food_name and quantity:
                food_entries.append({
                    "name": food_name, 
                    "quantity": quantity
                })
        
        # Submit Button
        submitted = st.form_submit_button("Record Meal")
    
    # Process form submission
    if submitted and food_entries:
        # Calculate nutritional information
        nutrition_info = calculate_nutritional_info(food_entries, food_dataset)
        
        # Handle unmatched foods
        if nutrition_info['unmatched_foods']:
            st.warning(f"Could not find nutritional information for: {', '.join(nutrition_info['unmatched_foods'])}")
        
        # Create a dataframe to store the meal
        meal_data = pd.DataFrame({
            'Date': [intake_date],
            'Meal Type': [meal_type],
            'Food Items': [nutrition_info['breakdown']],
            'Total Calories': [nutrition_info['total_calories']],
            'Protein (g)': [nutrition_info['total_protein']],
            'Carbohydrates (g)': [nutrition_info['total_carbs']],
            'Fat (g)': [nutrition_info['total_fat']]
        })
        
        # Append to existing CSV or create new
        try:
            existing_data = pd.read_csv('nutrition_log.csv')
            updated_data = pd.concat([existing_data, meal_data], ignore_index=True)
        except FileNotFoundError:
            updated_data = meal_data
        
        # Save to CSV
        updated_data.to_csv('nutrition_log.csv', index=False)
        
        # Display results
        st.success(f"Meal recorded for {intake_date}!")
        st.write(f"**Food Breakdown:** {nutrition_info['breakdown']}")
        st.write(f"**Total Calories:** {nutrition_info['total_calories']:.0f}")
        st.write(f"**Protein:** {nutrition_info['total_protein']:.1f}g")
        st.write(f"**Carbohydrates:** {nutrition_info['total_carbs']:.1f}g")
        st.write(f"**Fat:** {nutrition_info['total_fat']:.1f}g")
    
    # Nutrition Log Section
    st.header("Nutrition Log")
    try:
        nutrition_log = pd.read_csv('nutrition_log.csv')
        st.dataframe(nutrition_log)
        
        # Summary Statistics
        if st.button("Generate Summary Report"):
            st.subheader("Nutrition Summary")
            
            # Total Calories by Meal Type
            calories_by_meal = nutrition_log.groupby('Meal Type')['Total Calories'].sum()
            st.write("Total Calories by Meal Type:")
            st.bar_chart(calories_by_meal)
            
            # Average Nutritional Intake
            st.write("Average Daily Nutritional Intake:")
            avg_intake = nutrition_log.mean(numeric_only=True)
            st.dataframe(avg_intake)
            
            # Download Option
            csv = nutrition_log.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Full Nutrition Log",
                data=csv,
                file_name='nutrition_log.csv',
                mime='text/csv'
            )
    except FileNotFoundError:
        st.info("No nutrition log entries yet.")

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