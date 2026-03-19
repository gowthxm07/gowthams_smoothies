# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App Title & Description
st.title(":cup_with_straw: My Parents' healthy Dinner :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# ✅ FETCH BOTH COLUMNS + CONVERT TO PANDAS
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON")) \
    .to_pandas()

# Fruit list for multiselect
fruit_list = my_dataframe["FRUIT_NAME"].tolist()

# Customer Name Input
name_on_order = st.text_input("Name on Smoothie Order")

# Multi-select
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# ================= LOGIC =================
if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # ✅ LOOKUP SEARCH_ON VALUE
        search_on = my_dataframe.loc[
            my_dataframe["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write('Search value for', fruit_chosen, 'is', search_on)

        st.subheader(fruit_chosen + " Nutrition Information")

        # ✅ API CALL USING SEARCH_ON
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(
            smoothiefroot_response.json(),
            use_container_width=True
        )

    # INSERT AFTER LOOP
    my_insert_stmt = """ insert into smoothies.public.orders
        (name_on_order, ingredients)
        values ('""" + name_on_order + """','""" + ingredients_string + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
