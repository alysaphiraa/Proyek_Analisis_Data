import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set seaborn style for plots
sns.set(style='darkgrid')

# Load the dataset
day_df = pd.read_csv("https://raw.githubusercontent.com/alysaphiraa/Proyek_Analisis_Data/refs/heads/main/Dashboard/main_data.csv")

# Rename columns for better readability
day_df.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'cnt': 'count',
    'weathersit': 'weather_labels',
    'season': 'season_labels'
}, inplace=True)

# Ensure dateday is in datetime format
day_df['dateday'] = pd.to_datetime(day_df['dateday'])

# Map numerical values to meaningful labels
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

# Define functions to create dataframes for various visualizations
def create_daily_rent_df(df):
    return df.groupby(by='dateday').agg({'count': 'sum'}).reset_index()

def create_daily_casual_rent_df(df):
    if 'casual' in df.columns:
        return df.groupby(by='dateday').agg({'casual': 'sum'}).reset_index()
    return pd.DataFrame()

def create_daily_registered_rent_df(df):
    if 'registered' in df.columns:
        return df.groupby(by='dateday').agg({'registered': 'sum'}).reset_index()
    return pd.DataFrame()

def create_season_rent_df(df):
    return df.groupby(by='season_labels')[['registered', 'casual']].sum().reset_index()

def create_monthly_rent_df(df):
    monthly_rent_df = df.groupby(by='month').agg({'count': 'sum'})
    ordered_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return monthly_rent_df.reindex(ordered_months, fill_value=0)

def create_weekday_rent_df(df):
    return df.groupby(by='weekday').agg({'count': 'sum'}).reset_index()

def create_workingday_rent_df(df):
    return df.groupby(by='workingday').agg({'count': 'sum'}).reset_index()

def create_holiday_rent_df(df):
    return df.groupby(by='holiday').agg({'count': 'sum'}).reset_index()

def create_weather_rent_df(df):
    return df.groupby(by='weather_labels').agg({'count': 'sum'}).reset_index()

# Sidebar filters for date range
min_date = day_df['dateday'].min().date()
max_date = day_df['dateday'].max().date()

with st.sidebar:
    st.image('Dashboard/logo bike rentals.png')
    st.title('Bike Rentals Filters')

    # Date range filter
    start_date, end_date = st.date_input(
        label='Select Date Range',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Additional filters (e.g., Season, Weather)
    selected_seasons = st.multiselect(
        label="Select Seasons",
        options=day_df['season_labels'].unique(),
        default=day_df['season_labels'].unique()
    )

    selected_weathers = st.multiselect(
        label="Select Weather Conditions",
        options=day_df['weather_labels'].unique(),
        default=day_df['weather_labels'].unique()
    )

# Filter the dataset based on user inputs
main_df = day_df[
    (day_df['dateday'] >= pd.to_datetime(start_date)) & 
    (day_df['dateday'] <= pd.to_datetime(end_date)) &
    (day_df['season_labels'].isin(selected_seasons)) &
    (day_df['weather_labels'].isin(selected_weathers))
]

# Prepare data for various visualizations
daily_rent_df = create_daily_rent_df(main_df)
daily_casual_rent_df = create_daily_casual_rent_df(main_df)
daily_registered_rent_df = create_daily_registered_rent_df(main_df)
season_rent_df = create_season_rent_df(main_df)
monthly_rent_df = create_monthly_rent_df(main_df)
weekday_rent_df = create_weekday_rent_df(main_df)
workingday_rent_df = create_workingday_rent_df(main_df)
holiday_rent_df = create_holiday_rent_df(main_df)
weather_rent_df = create_weather_rent_df(main_df)

# Main Dashboard Section
st.title("Bike Rentals Dashboard")

# Daily Rentals
st.subheader('Daily Rentals Overview')
col1, col2, col3 = st.columns(3)

with col1:
    casual_rentals = daily_casual_rent_df['casual'].sum() if not daily_casual_rent_df.empty else 0
    st.metric('Casual Users', value=casual_rentals)

with col2:
    registered_rentals = daily_registered_rent_df['registered'].sum() if not daily_registered_rent_df.empty else 0
    st.metric('Registered Users', value=registered_rentals)

with col3:
    total_rentals = daily_rent_df['count'].sum()
    st.metric('Total Rentals', value=total_rentals)

# Monthly Rentals Plot
st.subheader('Monthly Rentals')

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly_rent_df.index, monthly_rent_df['count'], marker='o', linewidth=2, color='tab:blue')

# Add labels to the points
for index, row in monthly_rent_df.iterrows():
    ax.text(index, row['count'] + 100, str(row['count']), ha='center', va='bottom')

ax.set_xlabel('Month', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
ax.set_title('Rentals Per Month', fontsize=16)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# Rentals by Season
st.subheader('Rentals by Season')

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(x='season_labels', y='registered', data=season_rent_df, label='Registered', color='tab:green', ax=ax)
sns.barplot(x='season_labels', y='casual', data=season_rent_df, label='Casual', color='tab:blue', ax=ax)

for index, row in season_rent_df.iterrows():
    ax.text(index, row['registered'], str(row['registered']), ha='center', va='bottom', fontsize=10)
    ax.text(index, row['casual'], str(row['casual']), ha='center', va='bottom', fontsize=10)

ax.set_title('Rentals by Season', fontsize=16)
ax.set_xlabel('Season', fontsize=14)
ax.set_ylabel('Rentals', fontsize=14)
ax.legend()
plt.tight_layout()
st.pyplot(fig)

# Rentals by Weather
st.subheader('Rentals by Weather Conditions')

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='weather_labels', y='count', data=weather_rent_df, ax=ax)

for index, row in weather_rent_df.iterrows():
    ax.text(index, row['count'] + 100, str(row['count']), ha='center', va='bottom', fontsize=10)

ax.set_xlabel('Weather', fontsize=14)
ax.set_ylabel('Total Rentals', fontsize=14)
ax.set_title('Rentals by Weather', fontsize=16)
plt.tight_layout()
st.pyplot(fig)

# Rentals by Weekday, Working Day, and Holiday
st.subheader('Weekday, Working Day, and Holiday Rentals')

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 12))

# Weekday Rentals
sns.barplot(x='weekday', y='count', data=weekday_rent_df, ax=axes[0])
axes[0].set_title('Rentals by Weekday')

# Working Day Rentals
sns.barplot(x='workingday', y='count', data=workingday_rent_df, ax=axes[1])
axes[1].set_title('Rentals by Working Day')

# Holiday Rentals
sns.barplot(x='holiday', y='count', data=holiday_rent_df, ax=axes[2])
axes[2].set_title('Rentals by Holiday')

plt.tight_layout()
st.pyplot(fig)
