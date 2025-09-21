import pandas as pd
import psycopg2
import requests
from datetime import datetime

# -----------------------------
# Settings
# -----------------------------
DB_NAME = "retaildb"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_PASS = "yogita1400"       # UPDATED
DB_USER = "retailuser"
API_KEY = "99314d9e44c1f5051b6da9db46137fb2"  # UPDATED
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Location of the stores
STORE_LOCATIONS = {
    1: "Mumbai",
    2: "Delhi",
    3: "Bangalore",
    4: "Kolkata"
}

# -----------------------------
# Cleaning the data
# -----------------------------
df = pd.read_csv('sales.csv')
df['price'] = df['price'].fillna(df['price'].median())
df['quantity'] = df['quantity'].fillna(1)
df = df[(df['price'] > 0) & (df['quantity'] > 0)]
df = df.drop_duplicates()
print("Sales data loaded and cleaned.")
df.to_csv('cleaned_sales.csv', index=False)
print("Cleaned data saved to 'cleaned_sales.csv'")

# -----------------------------
# Fetching weather data
# -----------------------------
def fetch_weather(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        return temp, humidity
    else:
        print(f"Could not fetch weather for {city}. Status Code: {response.status_code}")
        return None, None

# Add weather data
temperatures = []
humidities = []

for idx, row in df.iterrows():
    store_id = row['store_id']
    city = STORE_LOCATIONS.get(store_id, "Mumbai")
    temp, humidity = fetch_weather(city)
    temperatures.append(temp)
    humidities.append(humidity)

df['temperature'] = temperatures
df['humidity'] = humidities

print("Weather data added to sales records.")

# -----------------------------
# Insert into PostgreSQL
# -----------------------------
conn = None
cursor = None

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,   # UPDATED
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("Connected to PostgreSQL.")

    # Create sales table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INT PRIMARY KEY,
            customer_id INT,
            product_id INT,
            store_id INT,
            quantity INT,
            price FLOAT,
            timestamp TIMESTAMP,
            temperature FLOAT,
            humidity FLOAT
        )
    ''')
    conn.commit()
    print("Table checked/created.")

    # Insert data from DataFrame 'df'
    for idx, row in df.iterrows():
        cursor.execute('''
            INSERT INTO sales (sale_id, customer_id, product_id, store_id, quantity, price, timestamp, temperature, humidity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sale_id) DO NOTHING
        ''', (
            int(row['sale_id']),
            int(row['customer_id']),
            int(row['product_id']),
            int(row['store_id']),
            int(row['quantity']),
            float(row['price']),
            datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S"),
            row['temperature'],
            row['humidity']
        ))
    conn.commit()
    print("Sales data inserted successfully.")

except Exception as e:
    print("Database error:", e)

finally:
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
    print("Database connection closed.")
