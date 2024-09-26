import streamlit as st
import numpy as np
import pandas as pd
import sqlite3
import datetime
import mysql
import pymysql
import sqlalchemy as sa




#QUESTION - CAN I REDUCE API CALLS TO 1?

st.set_page_config(layout="wide")
#title of application 
st.title(':green[Stoccoli] :broccoli:  ')

#connect to sql database
conn = sqlite3.connect('finance_app.db')
#set up engine, connection, cursor
engine = sa.create_engine('mysql+pymysql://admin:root1234@database-2.cbm2gcgo0w9n.us-east-2.rds.amazonaws.com:3306/financedb')
connection = engine.raw_connection()
conn = connection.cursor()



# Sidebar
st.sidebar.subheader('Query parameters')
start_date = st.sidebar.date_input("Start date", datetime.date(2019, 1, 7))
end_date = st.sidebar.date_input("End date", datetime.date(2024, 9, 23))
ticker_list = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/s-and-p-500-companies/master/data/constituents_symbols.txt')
tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol

#grab the industry and segment pertaining to the ticker
query = f"""
SELECT industry AS industry, sector as sector FROM company_data 
WHERE Ticker = '{tickerSymbol}';
"""
comp_data = pd.read_sql_query(query, connection)
industry = comp_data.iloc[0,0]
sector = comp_data.iloc[0,1]
st.write("Ticker:", tickerSymbol, "|    Industry:", industry, "|    Sector:", sector)

col1, col2 = st.columns(2)

with col1:
#STOCK CHART ---------------------------------------------------------------------------------------------
    #fetch data from input for stock line chart
    with st.container(height = 300, border=True):
        st.write("Stock Performance")
        query = f"""
        SELECT * FROM stock_price_data
        WHERE Ticker = '{tickerSymbol}' AND Date >= '{start_date}' AND Date <='{end_date}';
        """
        data = pd.read_sql_query(query, connection)
        a, b = st.columns([3,1])
        with a:
            with st.container(height=250, border=False):
                st.line_chart(data=data, x='Date', y=['Adj Close','sector_WASP','industry_WASP'], x_label=None, y_label=None, color=None, width=None, height=None, use_container_width=True)
        with b:
                with st.container(height=220, border=True):

#STOCK PERFORMANCE CARD------------------------------------------------------------------------------------
                    query = f"""
                    SELECT Date AS Date, `Adj Close` AS Close, sector_WASP AS `Sector Weighted Ave`,industry_WASP AS `Industry Weighted Ave` FROM stock_price_data
                    WHERE Ticker = '{tickerSymbol}' AND Date ='{end_date}';
                    """
                    stock_end = pd.read_sql_query(query, connection)
                    stock_end_price = "%.2f" % stock_end.iat[0,1]
                    stock_sect = "%.2f" % stock_end.iat[0,2]
                    stock_ind = "%.2f" % stock_end.iat[0,3]

                    query = f"""
                    SELECT Date AS Date, `Adj Close` AS Close, sector_WASP AS `Sector Weighted Ave`,industry_WASP AS `Industry Weighted Ave` FROM stock_price_data
                    WHERE Ticker = '{tickerSymbol}' AND Date ='{start_date}';
                    """
                    stock_start = pd.read_sql_query(query, connection)
                    stock_start_price = "%.2f" % stock_start.iat[0,1]
                    stock_sect_start = "%.2f" % stock_start.iat[0,2]
                    stock_ind_start = "%.2f" % stock_start.iat[0,3]

                    stock_perf = (float(stock_end.iat[0,1]) - float(stock_start.iat[0,1]))/float(stock_start.iat[0,1])
                    sect_perf = float((stock_end.iat[0,2]-stock_start.iat[0,2])/stock_start.iat[0,2])
                    ind_perf = float((stock_end.iat[0,3]-stock_start.iat[0,3])/stock_start.iat[0,3])
                    stock_delta_sect = stock_perf-sect_perf
                    stock_delta_ind = stock_perf-ind_perf

                    # st.write(stock_perf,sect_perf,ind_perf)
                    
                    st.metric(label="Stock Performance", value=(format(stock_perf,".0%")) , delta="")
                    st.metric(label="vs. Sector", value="", delta=format(stock_perf-sect_perf,".0%"))
                    st.metric(label="vs. Industry", value="", delta=format(stock_perf-ind_perf,".0%"))


#FINANCIAL PERFORMANCE CARDS---------------------------------------------------------------------------------
    with st.container(height = 300, border=True):
        st.write("Financial Performance")
        a, b, c, d = st.columns(4)

        # REVENUE-----------------------------------------------------------------------------
        #get sector info
        
        query = f"""
        SELECT sector AS sector, totalRevenue as totalRevenue FROM company_data
        WHERE sector = '{sector}' ;
        """
        sect_data = pd.DataFrame(pd.read_sql_query(query, connection))
        sect_median = int(sect_data.groupby(sect_data['sector']).median().iloc[0,0])
        sect_ave = int(sect_data.groupby(sect_data['sector']).mean().iloc[0,0])
        
        #get industry info

        query1 = f"""
        SELECT industry AS industry, totalRevenue as totalRevenue FROM company_data
        WHERE industry = '{industry}' ;
        """
        ind_data = pd.DataFrame(pd.read_sql_query(query1, connection))
        ind_median = int(ind_data.groupby(ind_data['industry']).median().iloc[0,0])
        ind_ave = int(ind_data.groupby(ind_data['industry']).mean().iloc[0,0])

        #get ticker specific info

        query2 = f"""
        SELECT totalRevenue as totalRevenue FROM company_data
        WHERE Ticker = '{tickerSymbol}'  ;
        """
        ticker_data = pd.DataFrame(pd.read_sql_query(query2, connection))
        company_t_eps = int(ticker_data.iloc[0])

        rev_company = company_t_eps
        rev_sect= sect_median
        rev_ind= ind_median

        with a:
            with st.container(height=220, border=True):
                st.metric(label="Total Revenue", value=format(company_t_eps) , delta="")
                st.metric(label="vs. Sector", value="", delta=format((company_t_eps-sect_median)/sect_median,".0%"))
                st.metric(label="vs. Industry", value="", delta=format((company_t_eps-ind_median)/ind_median,".0%"))


        #REVENUE GROWTH -----------------------------------------------------------------------------
        #get sector info
        query = f"""
        SELECT sector AS sector, revenueGrowth AS revenueGrowth FROM company_data
        WHERE sector = '{sector}' ;
        """
        sect_data = pd.DataFrame(pd.read_sql_query(query, connection))
        sect_median = float(sect_data.groupby(sect_data['sector']).median().iloc[0,0])
        sect_ave = float(sect_data.groupby(sect_data['sector']).mean().iloc[0,0])
        
        #get industry info

        query1 = f"""
        SELECT industry AS industry, revenueGrowth AS revenueGrowth FROM company_data
        WHERE industry = '{industry}' ;
        """
        ind_data = pd.DataFrame(pd.read_sql_query(query1, connection))
        ind_median = float(ind_data.groupby(ind_data['industry']).median().iloc[0,0])
        ind_ave = float(ind_data.groupby(ind_data['industry']).mean().iloc[0,0])

        #get ticker specific info

        query2 = f"""
        SELECT revenueGrowth AS revenueGrowth FROM company_data
        WHERE Ticker = '{tickerSymbol}'  ;
        """
        ticker_data = pd.DataFrame(pd.read_sql_query(query2, connection))
        company_t_eps = float(ticker_data.iloc[0])
        rev_growth_comp = company_t_eps
        rev_growth_sect = sect_median
        rev_growth_ind = ind_median

        with b:
            with st.container(height=220, border=True):
                st.metric(label="Revenue Growth", value=(format(company_t_eps,".0%")) , delta="")
                st.metric(label="vs. Sector", value="", delta=format(company_t_eps-sect_median,".0%"))
                st.metric(label="vs. Industry", value="", delta=format(company_t_eps-ind_median,".0%"))
        #OPERATING MARGINS -----------------------------------------------------------------------------
        #get sector info
        query = f"""
        SELECT sector AS sector, operatingMargins AS operatingMargins FROM company_data
        WHERE sector = '{sector}' ;
        """
        sect_data = pd.DataFrame(pd.read_sql_query(query, connection))
        sect_median = float(sect_data.groupby(sect_data['sector']).median().iloc[0,0])
        sect_ave = float(sect_data.groupby(sect_data['sector']).mean().iloc[0,0])
        
        #get industry info

        query1 = f"""
        SELECT industry AS industry, operatingMargins AS operatingMargins  FROM company_data
        WHERE industry = '{industry}' ;
        """
        ind_data = pd.DataFrame(pd.read_sql_query(query1, connection))
        ind_median = float(ind_data.groupby(ind_data['industry']).median().iloc[0,0])
        ind_ave = float(ind_data.groupby(ind_data['industry']).mean().iloc[0,0])

        #get ticker specific info

        query2 = f"""
        SELECT operatingMargins AS operatingMargins  FROM company_data
        WHERE Ticker = '{tickerSymbol}'  ;
        """
        ticker_data = pd.DataFrame(pd.read_sql_query(query2, connection))
        company_t_eps = float(ticker_data.iloc[0])

        with c:
            with st.container(height=220, border=True):
                st.metric(label="Operating Margins", value=format(company_t_eps,".0%"), delta="")
                st.metric(label="vs. Sector", value="", delta=(format(company_t_eps-sect_median,".0%")))
                st.metric(label="vs. Industry", value="", delta=(format(company_t_eps-ind_median,".0%")))      

        comp_op_marg = company_t_eps
        sect_op_marg = sect_median
        ind_op_marg = ind_median

        #EARNINGS GROWTH -----------------------------------------------------------------------------
        #get sector info
        query = f"""
        SELECT sector AS sector, earningsGrowth AS earningsGrowth FROM company_data
        WHERE sector = '{sector}' ;
        """
        sect_data = pd.DataFrame(pd.read_sql_query(query, connection))
        sect_median = float(sect_data.groupby(sect_data['sector']).median().iloc[0,0])
        sect_ave = float(sect_data.groupby(sect_data['sector']).mean().iloc[0,0])
        
        #get industry info

        query1 = f"""
        SELECT industry AS industry, earningsGrowth AS earningsGrowth  FROM company_data
        WHERE industry = '{industry}' ;
        """
        ind_data = pd.DataFrame(pd.read_sql_query(query1, connection))
        ind_median = float(ind_data.groupby(ind_data['industry']).median().iloc[0,0])
        ind_ave = float(ind_data.groupby(ind_data['industry']).mean().iloc[0,0])

        #get ticker specific info

        query2 = f"""
        SELECT earningsGrowth AS earningsGrowth  FROM company_data
        WHERE Ticker = '{tickerSymbol}'  ;
        """
        ticker_data = (pd.read_sql_query(query2, connection))
        company_t_eps = float(ticker_data.iloc[0])
        comp_earnings_growth = company_t_eps
        sect_earnings_growth = sect_median
        ind_earnings_growth = ind_median

        with d:
            with st.container(height=220, border=True):
                st.metric(label="Earnings Growth", value=format(company_t_eps,".0%") , delta="")
                st.metric(label="vs. Sector", value="", delta=format(company_t_eps-sect_median,".0%"))
                st.metric(label="vs. Industry", value="", delta=format(company_t_eps-ind_median,".0%"))   

        


    #INVESTMENT CONSIDERATIONS TAB    
        #GET SENTIMENT ANALYSIS-------------------------------------------------------------------------------------

with col2:
        

        with st.container(height=300, border=True):
            st.write("Investment Considerations")
            a, b, c, d = st.columns(4)
            query = f"""
            SELECT recommendationKey, recommendationMean, numberOfAnalystOpinions FROM company_data
            WHERE Ticker = '{tickerSymbol}'
            """
            sent_data = pd.DataFrame(pd.read_sql_query(query, connection))
            with a: 
                with st.container(height=220, border=True):
                    st.write("Sentiment:", sent_data.iloc[0,0].upper())
                    st.write("Rating / 5:", sent_data.iloc[0,1])
                    st.write("Analysts", sent_data.iloc[0,2])

            
# TRAILING PE METRIC-----------------------------------------------------------------
        #get sector info
            with b:
                query = f"""
                SELECT sector AS sector, trailingPE as trailingPE FROM company_data
                WHERE sector = '{sector}' ;
                """
                sect_data = pd.DataFrame(pd.read_sql_query(query, connection))
                sect_median = int(sect_data.groupby(sect_data['sector']).median().iloc[0,0])
                sect_ave = int(sect_data.groupby(sect_data['sector']).mean().iloc[0,0])
                
            #get industry info

                query1 = f"""
                SELECT industry AS industry, trailingPE as trailingPE FROM company_data
                WHERE industry = '{industry}' ;
                """
                ind_data = pd.DataFrame(pd.read_sql_query(query1, connection))
                ind_median = int(ind_data.groupby(ind_data['industry']).median().iloc[0,0])
                ind_ave = int(ind_data.groupby(ind_data['industry']).mean().iloc[0,0])

            #get ticker specific info

                query2 = f"""
                SELECT trailingPE as trailingPE FROM company_data
                WHERE Ticker = '{tickerSymbol}'  ;
                """
                ticker_data = pd.DataFrame(pd.read_sql_query(query2, connection))
                company_t_eps = int(ticker_data.iloc[0])
                with st.container(height=220, border=True):
                    st.metric(label="Trailing PE", value=(company_t_eps) , delta="")
                    st.metric(label="vs. Sector", value="", delta=company_t_eps-sect_median)
                    st.metric(label="vs. Industry", value="", delta=company_t_eps-ind_median)    

                comp_trailing = company_t_eps
                sect_trailing = sect_median
                Ind_trailing = ind_median
                discount_sect = (1-company_t_eps/sect_median)
                discount_ind = (1-company_t_eps/ind_median)
                
# SHARE RATIO METRIC-----------------------------------------------------------------
        #get sector info
            with c:
                query = f"""
                SELECT sector AS sector, shortRatio as shortRatio FROM company_data
                WHERE sector = '{sector}' ;
                """
                sect_data = pd.DataFrame(pd.read_sql_query(query, connection))
                sect_median = int(sect_data.groupby(sect_data['sector']).median().iloc[0,0])
                sect_ave = int(sect_data.groupby(sect_data['sector']).mean().iloc[0,0])
                
            #get industry info

                query1 = f"""
                SELECT industry AS industry, shortRatio as shortRatio FROM company_data
                WHERE industry = '{industry}' ;
                """
                ind_data = pd.DataFrame(pd.read_sql_query(query1, connection))
                ind_median = int(ind_data.groupby(ind_data['industry']).median().iloc[0,0])
                ind_ave = int(ind_data.groupby(ind_data['industry']).mean().iloc[0,0])

            #get ticker specific info

                query2 = f"""
                SELECT shortRatio as shortRatio FROM company_data
                WHERE Ticker = '{tickerSymbol}'  ;
                """
                ticker_data = pd.DataFrame(pd.read_sql_query(query2, connection))
                company_t_eps = int(ticker_data.iloc[0])
                with st.container(height=220, border=True):
                    st.metric(label="Short Ratio", value=(company_t_eps) , delta="")
                    st.metric(label="vs. Sector", value="", delta=company_t_eps-sect_median)
                    st.metric(label="vs. Industry", value="", delta=company_t_eps-ind_median)    


# sharesShort METRIC-----------------------------------------------------------------
        #get sector info
            with d:
                query = f"""
                SELECT sector AS sector, sharesShort FROM company_data
                WHERE sector = '{sector}' ;
                """
                sect_data = pd.DataFrame(pd.read_sql_query(query, connection))
                sect_median = int(sect_data.groupby(sect_data['sector']).median().iloc[0,0])
                sect_ave = int(sect_data.groupby(sect_data['sector']).mean().iloc[0,0])
                
            #get industry info

                query1 = f"""
                SELECT industry AS industry, sharesShort FROM company_data
                WHERE industry = '{industry}' ;
                """
                ind_data = pd.DataFrame(pd.read_sql_query(query1, connection))
                ind_median = int(ind_data.groupby(ind_data['industry']).median().iloc[0,0])
                ind_ave = int(ind_data.groupby(ind_data['industry']).mean().iloc[0,0])

            #get ticker specific info

                query2 = f"""
                SELECT sharesShort FROM company_data
                WHERE Ticker = '{tickerSymbol}'  ;
                """
                ticker_data = pd.DataFrame(pd.read_sql_query(query2, connection))
                company_t_eps = int(ticker_data.iloc[0])

                comp_short = company_t_eps
                sect_short = sect_median
                ind_short = ind_median

#sharesShortPriorMonth
                query = f"""
                SELECT sector AS sector, sharesShortPriorMonth FROM company_data
                WHERE sector = '{sector}' ;
                """
                sect_data_pm = pd.DataFrame(pd.read_sql_query(query, connection))
                sect_median_pm = int(sect_data_pm.groupby(sect_data_pm['sector']).median().iloc[0,0])
                sect_ave_pm = int(sect_data_pm.groupby(sect_data_pm['sector']).mean().iloc[0,0])
                
            #get industry info

                query1 = f"""
                SELECT industry AS industry, sharesShortPriorMonth FROM company_data
                WHERE industry = '{industry}' ;
                """
                ind_data_pm = pd.DataFrame(pd.read_sql_query(query1, connection))
                ind_median_pm = int(ind_data_pm.groupby(ind_data_pm['industry']).median().iloc[0,0])
                ind_ave_pm = int(ind_data_pm.groupby(ind_data_pm['industry']).mean().iloc[0,0])

            #get ticker specific info

                query2 = f"""
                SELECT sharesShortPriorMonth FROM company_data
                WHERE Ticker = '{tickerSymbol}'  ;
                """
                ticker_data_pm = pd.DataFrame(pd.read_sql_query(query2, connection))
                company_t_eps_pm = int(ticker_data.iloc[0])

                company_mom = (company_t_eps-company_t_eps_pm)/company_t_eps_pm
                sect_mom = company_mom - ((sect_median-sect_median_pm)/sect_median_pm)
                ind_mom = company_mom - ((ind_median-ind_median_pm)/ind_median_pm)


                with st.container(height=220, border=True):
                    st.metric(label="Short MoM", value=format(company_mom,".0%") , delta="")
                    st.metric(label="vs. Sector", value="", delta=format(sect_mom,".0%"))
                    st.metric(label="vs. Industry", value="", delta=format(ind_mom,".0%"))


#Narrative and stoccoli recommendation
        with st.container(height=300,border=True):  
                if (stock_delta_sect<0) and (stock_delta_ind<0) and (rev_growth_comp>rev_growth_sect) and (rev_growth_comp>rev_growth_ind) and (comp_earnings_growth>sect_earnings_growth) and (comp_earnings_growth>ind_earnings_growth):
                    st.write(':green[Stoccoli Reco] :broccoli:  ',"Buy that shiiiii")
                    st.write('This company is currently underperforming on stock returns but is outpacing the market in both revenue and earnings growth.  Likely an early signal for the broccoli about to dip in the cheddar')
                elif (stock_delta_sect>0) and (stock_delta_ind>0) and (rev_growth_comp<rev_growth_sect) and (rev_growth_comp<rev_growth_ind) and (comp_earnings_growth<sect_earnings_growth) and (comp_earnings_growth<ind_earnings_growth):
                    st.write(':green[Stoccoli Reco] :broccoli:  ',"Short that shiiiii")
                    st.write('This company is currently overperforming on stock returns but is losing ground to the market in both revenue and earnings growth.  Likely an early signal for the cheddar to fall off the broccoli')
                else:
                    st.write(':green[Stoccoli Reco] :broccoli:  ',"Hold on that shiii")
                    st.write('This company is a mixed bag.  If you want more certain', ':cheese_wedge:', 'seek it elsewhere')




                # a, b, c, d = st.columns(4)
                # with a: 
                #     if (stock_delta_sect>0) and (stock_delta_ind>0):
                #         st.write(tickerSymbol, "stock price has typically outperformed both the industry and the sector medians")
                #     elif (stock_delta_sect<0) and (stock_delta_ind<0):
                #         st.write(tickerSymbol, "stock price has typically underperformed both the industry and the sector medians")
                #     else:
                #         st.write(tickerSymbol, "stock price has typically performed between the industry and sector medians")


                # with b:

                #     if (rev_company>rev_sect) and (rev_company>rev_ind):
                #         st.write(tickerSymbol, "revenue is above both the sector and industry medians")
                #     elif (rev_company>rev_sect) or (rev_company>rev_ind):
                #         st.write(tickerSymbol, "revenue is between sector and industry medians")
                #     else:
                #         st.write(tickerSymbol, "revenue is smaller than both sect and industry medians")

                # with c:

                #     if (rev_growth_comp>rev_growth_sect) and (rev_growth_comp>rev_growth_ind):
                #         st.write(tickerSymbol, "revenue GROWTH is above both the sector and industry medians")
                #     elif (rev_growth_comp>rev_growth_sect) or (rev_growth_comp>rev_growth_ind):
                #         st.write(tickerSymbol, "revenue GROWTH is between sector and industry medians")
                #     else:
                #         st.write(tickerSymbol, "revenue GROWTH is smaller than both sect and industry medians")

                # with d:
                #     if (stock_delta_sect<0) and (stock_delta_ind<0) and (rev_growth_comp>rev_growth_sect) and (rev_growth_comp>rev_growth_ind) and (comp_earnings_growth>sect_earnings_growth) and (comp_earnings_growth>ind_earnings_growth):
                #         st.write(':green[Stoccoli] :broccoli:  ',"Buy that shiiiii")
                #     elif (stock_delta_sect>0) and (stock_delta_ind>0) and (rev_growth_comp<rev_growth_sect) and (rev_growth_comp<rev_growth_ind) and (comp_earnings_growth<sect_earnings_growth) and (comp_earnings_growth<ind_earnings_growth):
                #         st.write(':green[Stoccoli] :broccoli:  ',"Short that shiiiii")
                #     else:
                #         st.write(':green[Stoccoli] :broccoli:  ',"Hold on that shiii")