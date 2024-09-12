import streamlit as st
import numpy as np
import pandas as pd

#title of application 
st.title('Finance app')

#navigation sidebar
pg = st.navigation([st.Page("app.py"), st.Page("econ.py")])

st.sidebar.selectbox("Group", ["A","B","C"], key="group")
st.sidebar.slider("Size", 1, 5, key="size")
# "C:\Users\brads\FinanceApp\finance_app.db"

#connect to sql database
# url = "sqlite:///finance_app.db"
# .streamlit/secrets.toml
[connections.pets_db]
url = "sqlite:///pets.db"
# conn = st.connection('finance_db', type='sql')