# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Title
st.title(":cup_with_straw: My Parents' healthy Dinner :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit names
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Input
name_on_order = st.text_input("Name on Smoothie Order")

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Logic
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        st.subheader(fruit_chosen + " Nutrition Information")

        # ⭐ USING fruit_chosen VARIABLE DIRECTLY
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
        )

        st.dataframe(
            smoothiefroot_response.json(),
            use_container_width=True
        )

    # Insert
    my_insert_stmt = """ insert into smoothies.public.orders
        (name_on_order, ingredients)
        values ('""" + name_on_order + """','""" + ingredients_string + """')"""

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
