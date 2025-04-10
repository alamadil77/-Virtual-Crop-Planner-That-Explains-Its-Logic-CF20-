import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class CropRecommendationModel:
    def __init__(self):
        """Initialize the crop recommendation model."""
        self.model = None
        self.scaler = StandardScaler()
        self.features = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'month']
        self.trained = False
        self.crop_data = pd.read_csv('data/crop_data.csv')
        
    def prepare_training_data(self):
        """
        Prepare training data by extracting features from crop_data.
        """
        # Load crop data
        crop_data = self.crop_data.copy()
        
        # Create a synthetic dataset based on crop requirements
        rows = []
        for _, crop in crop_data.iterrows():
            # Generate multiple samples for each crop with slight variations in optimal conditions
            for _ in range(5):  # 5 samples per crop to create enough training data
                # Get midpoint of optimal ranges for each parameter
                nitrogen = crop['nitrogen_requirement'] * (0.9 + 0.2 * np.random.random())
                phosphorus = crop['phosphorus_requirement'] * (0.9 + 0.2 * np.random.random())
                potassium = crop['potassium_requirement'] * (0.9 + 0.2 * np.random.random())
                
                temp_mid = (crop['temperature_min'] + crop['temperature_max']) / 2
                temperature = temp_mid + np.random.normal(-2, 2)
                
                humidity_mid = (crop['humidity_min'] + crop['humidity_max']) / 2
                humidity = humidity_mid + np.random.normal(-5, 5)
                
                ph_mid = (crop['ph_min'] + crop['ph_max']) / 2
                ph = ph_mid + np.random.normal(-0.3, 0.3)
                
                rainfall_mid = (crop['rainfall_min'] + crop['rainfall_max']) / 2
                rainfall = rainfall_mid + np.random.normal(-10, 10)
                
                # Determine suitable month based on season
                if crop['season'] == 'kharif':
                    month = np.random.choice([6, 7, 8, 9])
                elif crop['season'] == 'rabi':
                    month = np.random.choice([10, 11, 12, 1, 2])
                elif crop['season'] == 'summer':
                    month = np.random.choice([3, 4, 5])
                else:  # annual
                    month = np.random.randint(1, 13)
                
                rows.append({
                    'nitrogen': max(0, nitrogen),
                    'phosphorus': max(0, phosphorus),
                    'potassium': max(0, potassium),
                    'temperature': max(0, temperature),
                    'humidity': max(0, humidity),
                    'ph': max(0, min(14, ph)),
                    'rainfall': max(0, rainfall),
                    'month': month,
                    'crop': crop['crop_name']
                })
                
                # Generate a few less optimal samples (lower probability of being recommended)
                if np.random.random() < 0.3:  # 30% chance of generating suboptimal sample
                    deviation = np.random.choice([-1, 1]) * np.random.uniform(0.3, 0.5)
                    factor = 1 + deviation
                    
                    rows.append({
                        'nitrogen': max(0, nitrogen * factor),
                        'phosphorus': max(0, phosphorus * factor),
                        'potassium': max(0, potassium * factor),
                        'temperature': max(0, temperature * (1 + deviation * 0.5)),
                        'humidity': max(0, humidity * (1 + deviation * 0.3)),
                        'ph': max(0, min(14, ph * (1 + deviation * 0.1))),
                        'rainfall': max(0, rainfall * (1 + deviation * 0.3)),
                        'month': month,
                        'crop': crop['crop_name']
                    })
        
        synthetic_data = pd.DataFrame(rows)
        
        # Split features and target
        X = synthetic_data[self.features]
        y = synthetic_data['crop']
        
        return X, y
    
    def train_model(self):
        """Train the random forest model for crop recommendation."""
        X, y = self.prepare_training_data()
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale the features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train the model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate the model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.trained = True
        return accuracy
    
    def predict(self, soil_params):
        """
        Predict the best crops for given soil parameters.
        
        Args:
            soil_params: Dict with keys matching self.features
            
        Returns:
            List of (crop, probability) tuples
        """
        if not self.trained:
            self.train_model()
        
        # Ensure all required features are present
        for feature in self.features:
            if feature not in soil_params and feature != 'month':
                raise ValueError(f"Missing required parameter: {feature}")
        
        # Convert input to DataFrame
        input_data = pd.DataFrame([soil_params])
        
        # Get features in correct order
        input_features = input_data[self.features]
        
        # Scale the input
        input_scaled = self.scaler.transform(input_features)
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(input_scaled)[0]
        
        # Get crop names
        crop_names = self.model.classes_
        
        # Create crop-probability pairs and sort
        recommendations = [(crop, prob) for crop, prob in zip(crop_names, probabilities)]
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    def get_feature_importance(self):
        """
        Get the importance of each feature in the model.
        
        Returns:
            Dict mapping feature names to importance scores
        """
        if not self.trained:
            self.train_model()
        
        importance_dict = {}
        for feature, importance in zip(self.features, self.model.feature_importances_):
            importance_dict[feature] = importance
        
        return importance_dict
    
    def explain_prediction(self, soil_params, top_crop):
        """
        Generate an explanation for why a crop was recommended.
        
        Args:
            soil_params: Dict of soil parameters
            top_crop: Name of the top recommended crop
            
        Returns:
            String explanation
        """
        if not self.trained:
            self.train_model()
        
        # Get the crop data for the recommended crop
        crop_data = self.crop_data[self.crop_data['crop_name'] == top_crop].iloc[0]
        
        # Compare soil parameters with crop requirements
        explanation_parts = []
        
        # Check nitrogen
        n_req = crop_data['nitrogen_requirement']
        n_actual = soil_params['nitrogen']
        if n_actual >= n_req * 0.9 and n_actual <= n_req * 1.1:
            explanation_parts.append(f"Your soil's nitrogen level ({n_actual:.1f}) is ideal for {top_crop}.")
        elif n_actual >= n_req * 0.7:
            explanation_parts.append(f"Your soil's nitrogen level ({n_actual:.1f}) is adequate for {top_crop}.")
        elif n_actual > n_req * 1.3:
            explanation_parts.append(f"Your soil's nitrogen level ({n_actual:.1f}) is higher than ideal for {top_crop}, but still acceptable.")
        else:
            explanation_parts.append(f"Your soil's nitrogen level ({n_actual:.1f}) is lower than ideal for {top_crop}, which needs about {n_req}.")
        
        # Check phosphorus
        p_req = crop_data['phosphorus_requirement']
        p_actual = soil_params['phosphorus']
        if p_actual >= p_req * 0.9 and p_actual <= p_req * 1.1:
            explanation_parts.append(f"Your soil's phosphorus level ({p_actual:.1f}) is ideal for {top_crop}.")
        elif p_actual >= p_req * 0.7:
            explanation_parts.append(f"Your soil's phosphorus level ({p_actual:.1f}) is adequate for {top_crop}.")
        elif p_actual > p_req * 1.3:
            explanation_parts.append(f"Your soil's phosphorus level ({p_actual:.1f}) is higher than ideal for {top_crop}, but still acceptable.")
        else:
            explanation_parts.append(f"Your soil's phosphorus level ({p_actual:.1f}) is lower than ideal for {top_crop}, which needs about {p_req}.")
        
        # Check potassium
        k_req = crop_data['potassium_requirement']
        k_actual = soil_params['potassium']
        if k_actual >= k_req * 0.9 and k_actual <= k_req * 1.1:
            explanation_parts.append(f"Your soil's potassium level ({k_actual:.1f}) is ideal for {top_crop}.")
        elif k_actual >= k_req * 0.7:
            explanation_parts.append(f"Your soil's potassium level ({k_actual:.1f}) is adequate for {top_crop}.")
        elif k_actual > k_req * 1.3:
            explanation_parts.append(f"Your soil's potassium level ({k_actual:.1f}) is higher than ideal for {top_crop}, but still acceptable.")
        else:
            explanation_parts.append(f"Your soil's potassium level ({k_actual:.1f}) is lower than ideal for {top_crop}, which needs about {k_req}.")
        
        # Check pH
        if soil_params['ph'] >= crop_data['ph_min'] and soil_params['ph'] <= crop_data['ph_max']:
            explanation_parts.append(f"Your soil's pH ({soil_params['ph']:.1f}) is in the ideal range for {top_crop}.")
        else:
            if soil_params['ph'] < crop_data['ph_min']:
                explanation_parts.append(f"Your soil's pH ({soil_params['ph']:.1f}) is slightly too acidic for {top_crop}, which prefers a pH of {crop_data['ph_min']}-{crop_data['ph_max']}.")
            else:
                explanation_parts.append(f"Your soil's pH ({soil_params['ph']:.1f}) is slightly too alkaline for {top_crop}, which prefers a pH of {crop_data['ph_min']}-{crop_data['ph_max']}.")
        
        # Check temperature if available
        if 'temperature' in soil_params:
            if soil_params['temperature'] >= crop_data['temperature_min'] and soil_params['temperature'] <= crop_data['temperature_max']:
                explanation_parts.append(f"The temperature ({soil_params['temperature']:.1f}°C) is in the ideal range for {top_crop}.")
            else:
                if soil_params['temperature'] < crop_data['temperature_min']:
                    explanation_parts.append(f"The temperature ({soil_params['temperature']:.1f}°C) is slightly cooler than ideal for {top_crop}, which prefers {crop_data['temperature_min']}-{crop_data['temperature_max']}°C.")
                else:
                    explanation_parts.append(f"The temperature ({soil_params['temperature']:.1f}°C) is slightly warmer than ideal for {top_crop}, which prefers {crop_data['temperature_min']}-{crop_data['temperature_max']}°C.")
        
        # Check season suitability based on month
        if 'month' in soil_params:
            month = soil_params['month']
            season_mapping = {
                'kharif': [6, 7, 8, 9],  # Jun-Sep
                'rabi': [10, 11, 12, 1, 2],  # Oct-Feb
                'summer': [3, 4, 5],  # Mar-May
                'annual': list(range(1, 13))  # All months
            }
            
            crop_season = crop_data['season']
            if month in season_mapping[crop_season] or crop_season == 'annual':
                explanation_parts.append(f"{top_crop} is well-suited for planting in month {month} (part of the {crop_season} season).")
            else:
                explanation_parts.append(f"While {top_crop} is typically a {crop_season} crop, it might still work in month {month} with some adjustments.")
        
        # Add growing days information
        explanation_parts.append(f"{top_crop} typically takes about {crop_data['growing_days']} days to grow until harvest.")
        
        # Combine all parts into a coherent explanation
        explanation = " ".join(explanation_parts)
        
        return explanation
