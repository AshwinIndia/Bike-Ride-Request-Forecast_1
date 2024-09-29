import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import make_column_transformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load the dataset
data = pd.read_csv('bike_demand_dataset.csv')

# Separate features and target
X = data.drop(columns=['demand', 'datetime'])
y = data['demand']

# Define columns to be transformed
numeric_features = ['temperature', 'humidity', 'hour_of_day', 'day_of_week', 'is_weekend', 'is_holiday']
categorical_features = ['weather_condition']

# Create a ColumnTransformer for preprocessing
preprocessor = make_column_transformer(
    (StandardScaler(), numeric_features),  # Scale numeric features
    (OneHotEncoder(handle_unknown='ignore'), categorical_features)  # One-hot encode categorical features
)

# Define the model pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor(n_estimators=100, random_state=42))
])

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model_pipeline.fit(X_train, y_train)

# Save the trained model
joblib.dump(model_pipeline, 'bike_demand_model.pkl')
print("Model saved as 'bike_demand_model.pkl'.")

sample_inputs = [
    {
        'temperature': 20.0,
        'humidity': 60.0,
        'weather_condition': 'Clear',
        'hour_of_day': 8,
        'day_of_week': 2,  
        'is_weekend': 0,   
        'is_holiday': 0    
    },
    {
        'temperature': 5.0,
        'humidity': 90.0,
        'weather_condition': 'Rainy',
        'hour_of_day': 17,
        'day_of_week': 4,  
        'is_weekend': 1,   
        'is_holiday': 0    
    },
    {
        'temperature': -2.0,
        'humidity': 80.0,
        'weather_condition': 'Snowy',
        'hour_of_day': 12,
        'day_of_week': 6,  
        'is_weekend': 1,   
        'is_holiday': 1    
    }
]

input_df = pd.DataFrame(sample_inputs)

retrained_model = joblib.load("bike_demand_model.pkl")

predicted_values = retrained_model.predict(input_df)

print(predicted_values)