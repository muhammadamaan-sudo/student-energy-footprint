import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

df = pd.read_csv("students.csv")

X = df[["distance_km", "meals", "laptop_hours", "mobile_hours"]]
y = df["total_co2"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "co2_model.pkl")
print("Regression model trained and saved")
