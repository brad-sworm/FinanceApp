import streamlit as st
import numpy as np
import pandas as pd
import sqlite3
import datetime
import mysql
import pymysql
import sqlalchemy as sa
import matplotlib.pyplot as plt



#QUESTION - CAN I REDUCE API CALLS TO 1?

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
        SELECT * FROM econ_data 
        WHERE Date >= '2000-01-01';
        """
    data = pd.read_sql_query(query, connection)
    fig, axs = plt.subplots(nrows=8, ncols=1, sharex =True,figsize=(10, 20))

    # Plot on the first subplot
    axs[0].plot(data['Date'], data['GDP'])
    axs[0].set_title('GDP')

    # Plot second subplot unemployment
    axs[1].plot(data['Date'], data['unemp_rate'])
    axs[1].set_title('Unemployment Rate')

    # Plot third subplot interest rate
    axs[2].plot(data['Date'], data['fed_funds_rate'])
    axs[2].set_title('Interest Rate')

        # Plot second subplot unemployment
    axs[3].plot(data['Date'], data['consumer_mortgage_orig'])
    axs[3].set_title('Mortgage Originations')

            # Plot second subplot unemployment
    axs[4].plot(data['Date'], data['consumer_mortgage_past_due'])
    axs[4].set_title('Mortgages past due')

        # Plot second subplot unemployment
    axs[5].plot(data['Date'], data['consumer_credit'])
    axs[5].set_title('Consumer Credit')

        # Plot second subplot unemployment
    axs[6].plot(data['Date'], data['consumer_credit_past_due'])
    axs[6].set_title('Consumer Credit Past Due')
            # Plot second subplot unemployment
    axs[7].plot(data['Date'], data['consumer_sentiment'])
    axs[7].set_title('Consumer Sentiment')
    # Display the subplots in Streamlit
    plt.subplots_adjust(wspace=0.0, hspace=.2)
    st.pyplot(fig)

    with y:
        st.write('note that this is likely a fools errand as many try and few, if any, are successful')
        st.write('however, here at stoccoli, we want to evaluate the company position snd determine if there is a sound pitch / hypothesis')
        st.write('to start this need to plot next to S&P and then evaluate correlations if they exist between single or multiple indicators AKA determine predictors')
        st.write('at the very least we can look predictions up or down and determine where wins / losses relative to the overall performance are expected to be beneficial vs. overall market')