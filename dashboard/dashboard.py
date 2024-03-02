import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style seaborn
sns.set(style='dark')

# Menyiapkan data day_rent_df
day_rent_df = pd.read_csv("dashboard/day.csv")
day_rent_df.head()

# Menghapus kolom yang tidak diperlukan
drop_col = ['windspeed']

for i in day_rent_df.columns:
  if i in drop_col:
    day_rent_df.drop(labels=i, axis=1, inplace=True)

# Mengubah nama judul kolom
day_rent_df.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'weathersit': 'weather_cond',
    'cnt': 'count'
}, inplace=True)

# Mengubah angka menjadi keterangan
day_rent_df['month'] = day_rent_df['month'].map({
    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
    7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
})
day_rent_df['season'] = day_rent_df['season'].map({
    1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
})
day_rent_df['weekday'] = day_rent_df['weekday'].map({
    0: 'Minggu', 1: 'Senin', 2: 'Selasa', 3: 'Rabu', 4: 'Kamis', 5: 'Jumat', 6: 'Sabtu'
})
day_rent_df['weather_cond'] = day_rent_df['weather_cond'].map({
    1: 'Cerah/Sebagian Berawan',
    2: 'Berkabut/Berawan',
    3: 'Salju Ringan/Hujan',
    4: 'Cuaca buruk'
})


# Menyiapkan daily_rental_df
def create_daily_rental_df(df):
    daily_rental_df = df.groupby(by='dateday').agg({
        'count': 'sum'
    }).reset_index()
    return daily_rental_df

# Menyiapkan daily_casual_rental_df
def create_daily_casual_rental_df(df):
    daily_casual_rental_df = df.groupby(by='dateday').agg({
        'casual': 'sum'
    }).reset_index()
    return daily_casual_rental_df

# Menyiapkan daily_registered_rental_df
def create_daily_registered_rental_df(df):
    daily_registered_rental_df = df.groupby(by='dateday').agg({
        'registered': 'sum'
    }).reset_index()
    return daily_registered_rental_df
    
# Menyiapkan season_rental_df
def create_season_rental_df(df):
    season_rental_df = df.groupby(by='season')[['registered', 'casual']].sum().reset_index()
    return season_rental_df

# Menyiapkan monthly_rent_df
def create_monthly_rental_df(df):
    monthly_rental_df = df.groupby(by='month').agg({
        'count': 'sum'
    })
    ordered_months = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    monthly_rental_df = monthly_rental_df.reindex(ordered_months, fill_value=0)
    return monthly_rental_df

# Menyiapkan weather_rental_df
def create_weather_rental_df(df):
    weather_rental_df = df.groupby(by='weather_cond').agg({
        'count': 'sum'
    })
    return weather_rental_df



# Membuat komponen filter
min_date = pd.to_datetime(day_rent_df['dateday']).dt.date.min()
max_date = pd.to_datetime(day_rent_df['dateday']).dt.date.max()
 
with st.sidebar:
    
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value= min_date,
        max_value= max_date,
        value=[min_date, max_date]
    )

main_df = day_rent_df[(day_rent_df['dateday'] >= str(start_date)) & 
                (day_rent_df['dateday'] <= str(end_date))]

# Menyiapkan berbagai dataframe
daily_rental_df = create_daily_rental_df(main_df)
daily_casual_rental_df = create_daily_casual_rental_df(main_df)
daily_registered_rental_df = create_daily_registered_rental_df(main_df)
season_rental_df = create_season_rental_df(main_df)
monthly_rental_df = create_monthly_rental_df(main_df)
weather_rental_df = create_weather_rental_df(main_df)


# Membuat Dashboard secara lengkap

# Membuat judul
st.header('Selamat Datang di Bike Rental 🚲')

# Membuat jumlah penyewaan harian
st.subheader('Daily Rentals')
col1, col2, col3 = st.columns(3)

with col1:
    daily_rent_casual = daily_casual_rental_df['casual'].sum()
    st.metric('Casual User', value= daily_rent_casual)

with col2:
    daily_rent_registered = daily_registered_rental_df['registered'].sum()
    st.metric('Registered User', value= daily_rent_registered)
 
with col3:
    daily_rent_total = daily_rental_df['count'].sum()
    st.metric('Total User', value= daily_rent_total)

# Membuat jumlah penyewaan bulanan
st.subheader('Monthly Rentals')
fig, ax = plt.subplots(figsize=(24, 8))
ax.plot(
    monthly_rental_df.index,
    monthly_rental_df['count'],
    marker='o', 
    linewidth=2,
    color='tab:blue'
)

for index, row in enumerate(monthly_rental_df['count']):
    ax.text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

ax.tick_params(axis='x', labelsize=25, rotation=45)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

# Membuat jumlah penyewaan berdasarkan season
st.subheader('Seasonly Rentals')

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    x='season',
    y='registered',
    data=season_rental_df,
    label='Registered',
    color='tab:blue',
    ax=ax
)

sns.barplot(
    x='season',
    y='casual',
    data=season_rental_df,
    label='Casual',
    color='tab:orange',
    ax=ax
)

for index, row in season_rental_df.iterrows():
    ax.text(index, row['registered'], str(row['registered']), ha='center', va='bottom', fontsize=12)
    ax.text(index, row['casual'], str(row['casual']), ha='center', va='bottom', fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20, rotation=0)
ax.tick_params(axis='y', labelsize=15)
ax.legend()
st.pyplot(fig)

# Membuah jumlah penyewaan berdasarkan kondisi cuaca
st.subheader('Weatherly Rentals')

fig, ax = plt.subplots(figsize=(16, 8))

colors=["tab:blue", "tab:orange", "tab:green"]

sns.barplot(
    x=weather_rental_df.index,
    y=weather_rental_df['count'],
    palette=colors,
    ax=ax
)

for index, row in enumerate(weather_rental_df['count']):
    ax.text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)


st.caption('Copyright (c) I Gusti Putu Oka Sugiarta 2024S')
