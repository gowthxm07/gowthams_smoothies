# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App Title & Description
st.title(":cup_with_straw: My Parents' healthy Dinner :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# New way to connect for SniS
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options table
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# Convert Snowpark dataframe → Python list
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Customer Name Input
name_on_order = st.text_input("Name on Smoothie Order")

# Multi-Select Widget
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# ================= LOGIC BLOCK =================
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # -------- NEW DYNAMIC API SECTION --------
        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )
        # ----------------------------------------

    # Build SQL Insert Statement (AFTER LOOP)
    my_insert_stmt = """ insert into smoothies.public.orders
            (name_on_order, ingredients)
            values ('""" + name_on_order + """','""" + ingredients_string + """')"""

    # Submit Button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
