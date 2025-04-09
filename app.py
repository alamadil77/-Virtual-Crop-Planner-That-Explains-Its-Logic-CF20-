from flask import Flask, request, jsonify
import pickle
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load model and encoders
with open("xgboost_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("encoders.pkl", "rb") as f:
    le_soil, le_season, le_crop = pickle.load(f)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    try:
        soil = le_soil.transform([data["soil"]])[0]
        season = le_season.transform([data["season"]])[0]
        rainfall = float(data["rainfall"])
        temperature = float(data["temperature"])

        features = np.array([[soil, season, rainfall, temperature]])
        prediction_encoded = model.predict(features)[0]
        prediction_label = le_crop.inverse_transform([prediction_encoded])[0]

        return jsonify({"crop": prediction_label})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
