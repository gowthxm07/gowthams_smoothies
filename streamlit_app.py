import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# 1. App Header
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# 2. User Input
name_on_order = st.text_input('Name on Smoothie Order')

# 3. Establish Connection
# Using st.connection handles the secrets logic for you
if 'cnx' not in st.session_state:
    st.session_state.cnx = st.connection("snowflake")

session = st.session_state.cnx.session()

# 4. Data Retrieval
# We wrap this in a try/except to give you a better error message if Snowflake rejects the query
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    pd_df = my_dataframe.to_pandas()
except Exception as e:
    st.error("Snowflake Query Failed. Check if your Warehouse is running and your Secrets are correct.")
    st.stop()

# 5. Multiselect Logic
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Get the search value for the API
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # API Call
        try:
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except:
            st.write(f"Could not find nutrition data for {fruit_chosen}.")

    # 6. Submission Logic
    my_insert_stmt = f""" insert into smoothies.public.orders(ingredients, name_on_order)
                values ('{ingredients_string}', '{name_on_order}')"""

    time_to_submit = st.button('Submit Order')

    if time_to_submit:
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        else:
            st.warning("Please enter a name for the order.")
