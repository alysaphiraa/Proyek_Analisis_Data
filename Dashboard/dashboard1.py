import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style seaborn
sns.set(style='dark')

# Menyiapkan data day_df
day_df = pd.read_csv(
    "https://raw.githubusercontent.com/alysaphiraa/Proyek_Analisis_Data/refs/heads/main/Dashboard/main_data.csv",
    parse_dates=['dteday']
)

# Mengubah nama judul kolom
day_df.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'cnt': 'count',
    'weathersit': 'weather_labels',
    'season': 'season_labels'
}, inplace=True)

# Mengubah angka menjadi keterangan
day_df['month'] = day_df['month'].map({
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
})
day_df['season_labels'] = day_df['season_labels'].map({
    1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
})
day_df['weekday'] = day_df['weekday'].map({
    0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'
})
day_df['weather_labels'] = day_df['weather_labels'].map({
    1: 'Clear',
    2: 'Mist',
    3: 'Light Rain',
    4: 'Heavy Rain'
})

# Define functions for data preparation
def create_daily_rent_df(df):
    daily_rent_df = df.groupby(by='dateday').agg({
        'count': 'sum'
    }).reset_index()
    return daily_rent_df

def create_season_rent_df(df):
    season_rent_df = df.groupby(by='season_labels')[['registered', 'casual']].sum().reset_index()
    return season_rent_df

def create_monthly_rent_df(df):
    monthly_rent_df = df.groupby(by='month').agg({
        'count': 'sum'
    })
    ordered_months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    monthly_rent_df = monthly_rent_df.reindex(ordered_months, fill_value=0)
    return monthly_rent_df

def create_weather_rent_df(df):
    weather_rent_df = df.groupby(by='weather_labels').agg({
        'count': 'sum'
    }).reset_index()
    return weather_rent_df

# Sidebar filters and logo
min_date = pd.to_datetime(day_df['dateday']).dt.date.min()
max_date = pd.to_datetime(day_df['dateday']).dt.date.max()

with st.sidebar:
    st.image('Dashboard/logo bike rentals.png')
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df['dateday'] >= str(start_date)) & 
                 (day_df['dateday'] <= str(end_date))]

# Data preparation
daily_rent_df = create_daily_rent_df(main_df)
season_rent_df = create_season_rent_df(main_df)
monthly_rent_df = create_monthly_rent_df(main_df)
weather_rent_df = create_weather_rent_df(main_df)

# Dashboard Title
st.header('Dashboard Bike Rentals')

# Daily Rentals
st.subheader('Daily Rentals')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric('Casual User', value=daily_rent_df['count'].sum())

# Monthly Rentals Plot
st.subheader('Monthly Rentals')
fig, ax = plt.subplots(figsize=(24, 8))
ax.plot(
    monthly_rent_df.index,
    monthly_rent_df['count'],
    marker='o', 
    linewidth=2,
    color='tab:blue'
)
ax.tick_params(axis='x', labelsize=25, rotation=45)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

# Rentals by Season Plot
st.subheader('Rentals by Season')
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x='season_labels', y='registered', data=season_rent_df, label='Registered', color='tab:green', ax=ax)
sns.barplot(x='season_labels', y='casual', data=season_rent_df, label='Casual', color='tab:blue', ax=ax)
ax.set_xlabel('Season', fontsize=15)
ax.set_ylabel('Rentals', fontsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.legend()
st.pyplot(fig)

# Rentals by Weather Plot
st.subheader('Rentals by Weather')
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x='weather_labels', y='count', data=weather_rent_df, ax=ax)
ax.set_xlabel('Weather Conditions', fontsize=15)
ax.set_ylabel('Rentals', fontsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)
