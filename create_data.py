import pandas as pd

data = {
    "distance_km": [5, 10, 2, 15, 8, 20],
    "meals": [3, 3, 2, 3, 3, 4],
    "laptop_hours": [4, 5, 3, 6, 4, 7],
    "mobile_hours": [3, 4, 2, 5, 3, 6]
}

df = pd.DataFrame(data)

# Simple CO2 formula (used only to generate training target)
df["total_co2"] = (
    df["distance_km"] * 0.18 +
    df["meals"] * 2.5 +
    df["laptop_hours"] * 0.05 +
    df["mobile_hours"] * 0.01
)

df.to_csv("students.csv", index=False)
print("students.csv created")
