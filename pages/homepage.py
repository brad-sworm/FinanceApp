import streamlit as st
import numpy as np
import pandas as pd
import sqlite3
import datetime
import mysql
import pymysql
import sqlalchemy as sa
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")
#title of application 
st.title(':green[Stoccoli] :broccoli:  ')

#set up engine, connection, cursor
engine = sa.create_engine('mysql+pymysql://admin:root1234@database-2.cbm2gcgo0w9n.us-east-2.rds.amazonaws.com:3306/financedb')
connection = engine.raw_connection()
conn = connection.cursor()

x, y = st.columns(2)
with x:
    query = f"""
        SELECT * FROM boolean_algo
        WHERE stoccoli_reco = 'Buy';
        """
    data = pd.read_sql_query(query, connection)
    df = data.sort_values(by=['ave_upside'])
    st.write(':green[Stoccoli] :broccoli: BUY :cheese_wedge: :cheese_wedge: :cheese_wedge:')
    st.bar_chart(data=df, x='ave_upside',y='Ticker')

with y:
    query = f"""
        SELECT * FROM boolean_algo
        WHERE stoccoli_reco = 'Short';
        """
    data = pd.read_sql_query(query, connection)
    df = data.sort_values(by=['ave_upside'])
    st.write(':green[Stoccoli] :broccoli: SHORT :cheese_wedge: :cheese_wedge: :cheese_wedge:')
    st.bar_chart(data=df, x='ave_upside',y='Ticker')
