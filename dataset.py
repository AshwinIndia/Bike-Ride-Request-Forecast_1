import pandas as pd
import numpy as np

# Set a random seed for reproducibility
np.random.seed(42)

# Generate datetime range
dates = pd.date_range(start='2024-01-01', end='2024-08-31 23:00:00', freq='H')
n_samples = len(dates)

# Generate synthetic weather data
temperature = np.random.normal(15, 10, size=n_samples)  # Mean = 15°C, Stddev = 10
humidity = np.random.uniform(30, 100, size=n_samples)   # Uniform distribution between 30% and 100%
weather_condition = np.random.choice(
    ['Clear', 'Rainy', 'Snowy', 'Cloudy'], size=n_samples, 
    p=[0.6, 0.2, 0.1, 0.1]
)  # Probabilities for weather conditions

# Extract time-based features
hour_of_day = dates.hour
day_of_week = dates.dayofweek
is_weekend = (day_of_week >= 5).astype(int)  # 1 if Saturday or Sunday, else 0
is_holiday = (np.random.rand(n_samples) < 0.05).astype(int)  # Randomly assign 5% holidays

# Generate synthetic demand
base_demand = 50 + 2 * temperature - 0.5 * humidity
base_demand += (hour_of_day >= 7) & (hour_of_day <= 9) * 10  # Morning rush hour
base_demand += (hour_of_day >= 17) & (hour_of_day <= 19) * 20  # Evening rush hour
base_demand -= is_weekend * 30  # Lower demand on weekends
base_demand += (weather_condition == 'Clear') * 50  # Higher demand when clear
base_demand -= (weather_condition == 'Rainy') * 40  # Lower demand when rainy
base_demand += np.random.normal(0, 10, size=n_samples)  # Add noise

# Ensure positive demand values
demand = np.maximum(base_demand, 0).astype(int)

# Create a DataFrame
data = pd.DataFrame({
    'datetime': dates,
    'temperature': temperature,
    'humidity': humidity,
    'weather_condition': weather_condition,
    'hour_of_day': hour_of_day,
    'day_of_week': day_of_week,
    'is_weekend': is_weekend,
    'is_holiday': is_holiday,
    'demand': demand
})

# Save to CSV
data.to_csv('bike_demand_dataset.csv', index=False)
print("Dataset saved as 'bike_demand_dataset.csv'.")
