import pandas as pd
import streamlit as st
import plotly.express as px


st.title('The Historical data on the daily number of new reported COVID-19 cases EU/EEA')

# read COVID19 data
df_COVID19 = pd.read_csv('./csv_data/data.csv')
# read location data
col_names = ['country_code', 'name_jp', 'name_jps', 'capital_jp', 'name_en', 'name_ens', 'capital_en', 'lat', 'lon']
df_latlon = pd.read_csv('./csv_data/r0304world_utf8.csv', sep='\t')

# Pre-process such as deleting missing data
df_COVID19.dropna(subset=['geoId'], inplace=True)
df_COVID19.dropna(subset=['countryterritoryCode'], inplace=True)

df_latlon_new = df_latlon.rename(columns={'country_code':'geoId'})
df_latlon_new = df_latlon_new.drop(['name_jp', 'name_jps', 'capital_jp'], axis=1)

df_latlon_new.replace('GB', 'UK', inplace=True)
df_latlon_new.replace('GR', 'EL', inplace=True)

# merge
df_new = pd.merge(df_COVID19, df_latlon_new, on='geoId', how='outer', indicator=True)
df_new2 = df_new[df_new['_merge']=='both']

# change data format of 'dataRep' to YYYY-MM-DD and sort
df_new2['dateRep'] = pd.to_datetime(df_new2['dateRep'], format='%d/%m/%Y').dt.date
#df_new2['dateRep'].dt.strftime('%Y/%m/%d')
df_new2['cases'] = df_new2['cases'].where(df_new2['cases'] > 0, 0 )
df_new2['deaths'] = df_new2['deaths'].where(df_new2['deaths'] > 0, 0 )
df_new3 = df_new2.sort_values(['countriesAndTerritories', 'dateRep'], ascending=True)
#print(df_new3.dtypes)

st.header('COVID-19 infected person transition data')
# plot data by 'plotly.express'
fig1 = px.line(
    df_new3,
    x="dateRep",
    y="cases",
    color="countriesAndTerritories",
)
st.plotly_chart(fig1)

st.header('COVID-19 deaths transition data')
# plot data by 'plotly.express'
fig2 = px.line(
    df_new3,
    x="dateRep",
    y="deaths",
    color="countriesAndTerritories",
)
st.plotly_chart(fig2)


st.header('Bubble Map of Last 30 days')
# plot data by 'plotly.express'
dateRep_list = df_new3['dateRep'].unique()
dateRep_list.sort()
dateRep_list_last30 = dateRep_list[-30:-1]

option_dateRep = st.selectbox(
    'dateRep',
    (dateRep_list_last30)
)

df = df_new3[df_new3['dateRep'] == option_dateRep ]
fig3 = px.scatter_geo(df, lat='lat', lon='lon', color="countriesAndTerritories",
                      hover_name="countriesAndTerritories", size="cases",
                      projection="natural earth")
fig3.update_layout(
    geo_scope='europe', # limite map scope to Europe
)
st.plotly_chart(fig3)

#
st.text('首都の緯度経度データの出典：アマノ技研')
st.text('本結果はEuropean Centre for Disease Prevention and Controlのデータを加工して作成')

