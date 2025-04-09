import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataProcessor:
    def __init__(self):
        """Initialize the DataProcessor class to handle data loading and preprocessing."""
        self.crop_data = None
        self.market_data = None
        self.soil_params_range = {
            'nitrogen': (0, 200),
            'phosphorus': (0, 150),
            'potassium': (0, 200),
            'ph': (0, 14),
            'temperature': (0, 45),
            'humidity': (0, 100),
            'rainfall': (0, 300)
        }
        self.season_mapping = {
            'kharif': [6, 7, 8, 9],  # Jun-Sep
            'rabi': [10, 11, 12, 1, 2],  # Oct-Feb
            'summer': [3, 4, 5],  # Mar-May
            'annual': list(range(1, 13))  # All months
        }
        self.load_data()
        
    def load_data(self):
        """Load crop and market data from CSV files."""
        try:
            self.crop_data = pd.read_csv('data/crop_data.csv')
            self.market_data = pd.read_csv('data/market_data.csv')
            print(f"Data loaded successfully: {len(self.crop_data)} crops, {len(self.market_data)} market entries")
        except Exception as e:
            print(f"Error loading data: {e}")
            # Create empty dataframes with expected columns if loading fails
            self.crop_data = pd.DataFrame(columns=[
                'crop_name', 'nitrogen_requirement', 'phosphorus_requirement', 
                'potassium_requirement', 'temperature_min', 'temperature_max',
                'rainfall_min', 'rainfall_max', 'humidity_min', 'humidity_max',
                'ph_min', 'ph_max', 'season', 'growing_days'
            ])
            self.market_data = pd.DataFrame(columns=[
                'crop_name', 'month', 'year', 'price_per_kg', 
                'demand_score', 'supply_score', 'profit_potential'
            ])
            
    def get_current_season(self, month):
        """Determine the current growing season based on the month."""
        for season, months in self.season_mapping.items():
            if month in months:
                return season
        return 'unknown'
    
    def filter_crops_by_season(self, month, include_annual=True):
        """Filter crops that are suitable for planting in the given month."""
        current_season = self.get_current_season(month)
        if include_annual:
            return self.crop_data[
                (self.crop_data['season'] == current_season) | 
                (self.crop_data['season'] == 'annual')
            ]
        return self.crop_data[self.crop_data['season'] == current_season]
    
    def get_soil_compatibility_score(self, crop, soil_params):
        """
        Calculate how compatible a crop is with given soil parameters.
        Returns a score between 0 and 1, where 1 is perfectly compatible.
        """
        # Check if all required soil parameters are present
        if not all(k in soil_params for k in ['nitrogen', 'phosphorus', 'potassium', 'ph']):
            return 0
        
        # Calculate compatibility for each parameter
        n_score = self._get_nutrient_score(soil_params['nitrogen'], crop['nitrogen_requirement'])
        p_score = self._get_nutrient_score(soil_params['phosphorus'], crop['phosphorus_requirement'])
        k_score = self._get_nutrient_score(soil_params['potassium'], crop['potassium_requirement'])
        
        # Calculate pH compatibility
        ph_score = 0
        if crop['ph_min'] <= soil_params['ph'] <= crop['ph_max']:
            ph_score = 1
        else:
            # Decreasing score based on distance from optimal range
            min_distance = min(abs(soil_params['ph'] - crop['ph_min']), 
                            abs(soil_params['ph'] - crop['ph_max']))
            ph_score = max(0, 1 - (min_distance / 2))  # Reduce score by distance, max penalty of 2 pH units
            
        # Optional parameters with defaults
        temp_score = 1
        humidity_score = 1
        rainfall_score = 1
        
        if 'temperature' in soil_params:
            if crop['temperature_min'] <= soil_params['temperature'] <= crop['temperature_max']:
                temp_score = 1
            else:
                min_distance = min(abs(soil_params['temperature'] - crop['temperature_min']), 
                                abs(soil_params['temperature'] - crop['temperature_max']))
                temp_score = max(0, 1 - (min_distance / 10))  # Reduce score by distance
                
        if 'humidity' in soil_params:
            if crop['humidity_min'] <= soil_params['humidity'] <= crop['humidity_max']:
                humidity_score = 1
            else:
                min_distance = min(abs(soil_params['humidity'] - crop['humidity_min']), 
                                abs(soil_params['humidity'] - crop['humidity_max']))
                humidity_score = max(0, 1 - (min_distance / 20))  # Reduce score by distance
                
        if 'rainfall' in soil_params:
            if crop['rainfall_min'] <= soil_params['rainfall'] <= crop['rainfall_max']:
                rainfall_score = 1
            else:
                min_distance = min(abs(soil_params['rainfall'] - crop['rainfall_min']), 
                                abs(soil_params['rainfall'] - crop['rainfall_max']))
                rainfall_score = max(0, 1 - (min_distance / 50))  # Reduce score by distance
        
        # Combined score with weighted parameters
        weights = {
            'n_score': 0.2,
            'p_score': 0.15,
            'k_score': 0.15,
            'ph_score': 0.2,
            'temp_score': 0.1,
            'humidity_score': 0.1,
            'rainfall_score': 0.1
        }
        
        total_score = (weights['n_score'] * n_score + 
                       weights['p_score'] * p_score + 
                       weights['k_score'] * k_score + 
                       weights['ph_score'] * ph_score + 
                       weights['temp_score'] * temp_score + 
                       weights['humidity_score'] * humidity_score + 
                       weights['rainfall_score'] * rainfall_score)
        
        return total_score
    
    def _get_nutrient_score(self, soil_value, crop_requirement):
        """Calculate how well the soil nutrient level meets the crop requirement."""
        if soil_value >= crop_requirement:
            # If soil has enough or more nutrients than required
            # Too much can also be less optimal, so we decrease the score if it's significantly higher
            if soil_value > crop_requirement * 2:
                return max(0.5, 1 - ((soil_value - (crop_requirement * 2)) / (crop_requirement * 2)))
            return 1.0
        else:
            # If soil has less nutrients than required
            return soil_value / crop_requirement
    
    def get_market_data_for_crop(self, crop_name, month=None, year=None):
        """Get the latest market data for a specific crop."""
        if month is None or year is None:
            # Get the most recent data
            data = self.market_data[self.market_data['crop_name'] == crop_name]
            if data.empty:
                return None
            # Sort by year and month to get the most recent
            data = data.sort_values(by=['year', 'month'], ascending=False)
            return data.iloc[0]
        else:
            # Get data for specific month and year
            data = self.market_data[
                (self.market_data['crop_name'] == crop_name) &
                (self.market_data['month'] == month) &
                (self.market_data['year'] == year)
            ]
            if data.empty:
                return None
            return data.iloc[0]
    
    def get_market_score(self, crop_name, month, year=2023):
        """
        Calculate a market score for a crop based on price, demand, and supply.
        Returns a score between 0 and 1.
        """
        market_data = self.get_market_data_for_crop(crop_name, month, year)
        if market_data is None:
            return 0.5  # Neutral score if no data
        
        # Normalize price (higher price = better score)
        all_prices = self.market_data['price_per_kg']
        normalized_price = (market_data['price_per_kg'] - all_prices.min()) / (all_prices.max() - all_prices.min())
        
        # Consider demand and supply scores (1-10 scale in original data)
        demand_score = market_data['demand_score'] / 10  # Convert to 0-1 scale
        supply_score = 1 - (market_data['supply_score'] / 10)  # Invert so low supply = higher score
        
        # Direct profit potential score
        profit_score = market_data['profit_potential'] / 10  # Convert to 0-1 scale
        
        # Combine scores with weights
        weights = {
            'price': 0.3,
            'demand': 0.3,
            'supply': 0.2,
            'profit': 0.2
        }
        
        total_score = (weights['price'] * normalized_price + 
                      weights['demand'] * demand_score +
                      weights['supply'] * supply_score +
                      weights['profit'] * profit_score)
        
        return total_score

    def get_combined_score(self, crop, soil_params, month, year=2023):
        """
        Calculate a combined score considering soil compatibility and market factors.
        Returns a score between 0 and 1.
        """
        soil_score = self.get_soil_compatibility_score(crop, soil_params)
        market_score = self.get_market_score(crop['crop_name'], month, year)
        
        # Combine scores with weights
        # Give more weight to soil compatibility as it's more fundamental
        soil_weight = 0.6
        market_weight = 0.4
        
        return (soil_weight * soil_score) + (market_weight * market_score)
    
    def get_top_recommendations(self, soil_params, month, year=2023, limit=5):
        """
        Get the top crop recommendations based on soil and market factors.
        Returns a list of dictionaries with crop information and scores.
        """
        season_crops = self.filter_crops_by_season(month)
        if season_crops.empty:
            return []
        
        recommendations = []
        
        for _, crop in season_crops.iterrows():
            combined_score = self.get_combined_score(crop, soil_params, month, year)
            soil_score = self.get_soil_compatibility_score(crop, soil_params)
            market_score = self.get_market_score(crop['crop_name'], month, year)
            
            recommendations.append({
                'crop_name': crop['crop_name'],
                'combined_score': combined_score,
                'soil_score': soil_score,
                'market_score': market_score,
                'season': crop['season'],
                'growing_days': crop['growing_days']
            })
        
        # Sort by combined score and return top N
        recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
        return recommendations[:limit]
