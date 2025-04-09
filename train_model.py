import pandas as pd
import xgboost as xgb
import pickle
from sklearn.preprocessing import LabelEncoder

# Load and normalize column names
df = pd.read_csv("crop_requirements.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print("✅ Cleaned column names:", list(df.columns))

# Rename columns to match expected names
expected_columns = {
    "soil_type": "soil",
    "optimal_rainfall_(mm)": "rainfall",
    "optimal_temperature_(°c)": "temperature"
}
df = df.rename(columns=expected_columns)

# Validate column availability
required = ["soil", "season", "rainfall", "temperature", "crop"]
if not all(col in df.columns for col in required):
    raise Exception(f"❌ Required columns missing. Found: {list(df.columns)}")

# Encode categorical data
le_soil = LabelEncoder()
le_season = LabelEncoder()
le_crop = LabelEncoder()

df["soil"] = le_soil.fit_transform(df["soil"])
df["season"] = le_season.fit_transform(df["season"])
df["crop"] = le_crop.fit_transform(df["crop"])

# Train the model
X = df[["soil", "season", "rainfall", "temperature"]]
y = df["crop"]
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
model.fit(X, y)

# Save model and all encoders
with open("xgboost_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("encoders.pkl", "wb") as f:
    pickle.dump((le_soil, le_season, le_crop), f)

print("✅ Model trained and saved successfully!")
