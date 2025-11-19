import streamlit as st
import requests
from snowflake.snowpark.functions import col
import pandas as pd

st.title("Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection('snowflake')
session = cnx.session()

# Load the FRUIT_OPTIONS table
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convert to pandas for easier indexing
pd_df = my_dataframe.to_pandas()

# Create a simple list of fruit names for the multiselect
fruit_names = pd_df["FRUIT_NAME"].tolist()

# Multiselect widget
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

# If user selected ingredients
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Build ingredients string for DB insert
        ingredients_string += fruit_chosen + " "

        # Lookup SEARCH_ON value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Section title
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Correct API call using f-string
        url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        smoothiefroot_response = requests.get(url)

        # Display returned JSON
        st.dataframe(smoothiefroot_response.json(), use_container_width=True)

    # Prepare SQL for inserting the order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}');
    """

    # Submit button
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
