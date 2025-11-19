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

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# DEBUG
st.write("DEBUG: loaded dataframe with rows:", len(pd_df))

# Create list for multiselect
fruit_names = pd_df["FRUIT_NAME"].tolist()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

# If ingredients selected
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        # Build ingredients string
        ingredients_string += fruit_chosen + " "

        # Lookup SEARCH_ON
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # API call
        url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        smoothiefroot_response = requests.get(url)

        st.dataframe(smoothiefroot_response.json(), use_container_width=True)

    # Insert order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}');
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
