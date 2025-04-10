import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

class MarketTrendAnalyzer:
    def __init__(self):
        """Initialize the market trend analyzer."""
        self.market_data = None
        self.load_data()
        
    def load_data(self):
        """Load market data from the CSV file."""
        try:
            self.market_data = pd.read_csv('data/market_data.csv')
            print(f"Market data loaded successfully: {len(self.market_data)} entries")
        except Exception as e:
            print(f"Error loading market data: {e}")
            # Create an empty DataFrame with expected columns
            self.market_data = pd.DataFrame(columns=[
                'crop_name', 'month', 'year', 'price_per_kg', 
                'demand_score', 'supply_score', 'profit_potential'
            ])
    
    def get_price_trend(self, crop_name, year=2023):
        """
        Get price trend data for a specific crop.
        
        Args:
            crop_name: Name of the crop
            year: Year to analyze, defaults to 2023
            
        Returns:
            DataFrame with monthly prices
        """
        # Filter data for the specified crop and year
        crop_data = self.market_data[
            (self.market_data['crop_name'] == crop_name) & 
            (self.market_data['year'] == year)
        ]
        
        # Sort by month
        crop_data = crop_data.sort_values('month')
        
        return crop_data[['month', 'price_per_kg']]
    
    def get_market_metrics(self, crop_name, month, year=2023):
        """
        Get comprehensive market metrics for a crop.
        
        Args:
            crop_name: Name of the crop
            month: Month (1-12)
            year: Year, defaults to 2023
            
        Returns:
            Dict with market metrics or None if data not found
        """
        # Get data for the specified crop, month, and year
        data = self.market_data[
            (self.market_data['crop_name'] == crop_name) & 
            (self.market_data['month'] == month) & 
            (self.market_data['year'] == year)
        ]
        
        if data.empty:
            return None
        
        # Extract the first (should be only) row
        row = data.iloc[0]
        
        return {
            'price_per_kg': row['price_per_kg'],
            'demand_score': row['demand_score'],
            'supply_score': row['supply_score'],
            'profit_potential': row['profit_potential']
        }
    
    def get_top_profitable_crops(self, month, year=2023, limit=5):
        """
        Get the top most profitable crops for a given month and year.
        
        Args:
            month: Month (1-12)
            year: Year, defaults to 2023
            limit: Number of crops to return, defaults to 5
            
        Returns:
            List of dicts with crop information
        """
        # Filter data for the specified month and year
        data = self.market_data[
            (self.market_data['month'] == month) & 
            (self.market_data['year'] == year)
        ]
        
        if data.empty:
            return []
        
        # Sort by profit potential (descending)
        data = data.sort_values('profit_potential', ascending=False)
        
        # Return top N crops
        top_crops = []
        for _, row in data.head(limit).iterrows():
            top_crops.append({
                'crop_name': row['crop_name'],
                'price_per_kg': row['price_per_kg'],
                'demand_score': row['demand_score'],
                'supply_score': row['supply_score'],
                'profit_potential': row['profit_potential']
            })
        
        return top_crops
    
    def generate_price_chart(self, crop_name, year=2023):
        """
        Generate a price chart for a specific crop.
        
        Args:
            crop_name: Name of the crop
            year: Year to analyze, defaults to 2023
            
        Returns:
            Base64-encoded image of the chart
        """
        # Get price trend data
        price_data = self.get_price_trend(crop_name, year)
        
        if price_data.empty:
            return None
        
        # Create figure
        plt.figure(figsize=(10, 5))
        plt.plot(price_data['month'], price_data['price_per_kg'], marker='o', linestyle='-', color='#1f77b4')
        plt.title(f'Price Trend for {crop_name.capitalize()} in {year}')
        plt.xlabel('Month')
        plt.ylabel('Price (Rs/kg)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(range(1, 13))
        
        # Save figure to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Encode the image to base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str
    
    def generate_market_comparison(self, crop_names, month, year=2023):
        """
        Generate a comparison chart for multiple crops.
        
        Args:
            crop_names: List of crop names
            month: Month (1-12)
            year: Year, defaults to 2023
            
        Returns:
            Base64-encoded image of the chart
        """
        # Initialize data lists
        prices = []
        demand_scores = []
        supply_scores = []
        profit_potentials = []
        
        # Collect data for each crop
        for crop in crop_names:
            metrics = self.get_market_metrics(crop, month, year)
            if metrics:
                prices.append(metrics['price_per_kg'])
                demand_scores.append(metrics['demand_score'])
                supply_scores.append(metrics['supply_score'])
                profit_potentials.append(metrics['profit_potential'])
            else:
                # Use placeholder values if data not available
                prices.append(0)
                demand_scores.append(0)
                supply_scores.append(0)
                profit_potentials.append(0)
        
        # Format crop names for display (capitalize)
        formatted_crop_names = [name.replace('_', ' ').capitalize() for name in crop_names]
        
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        
        # Price subplot
        axs[0, 0].bar(formatted_crop_names, prices, color='#1f77b4')
        axs[0, 0].set_title('Price (Rs/kg)')
        axs[0, 0].tick_params(axis='x', rotation=45)
        
        # Demand subplot
        axs[0, 1].bar(formatted_crop_names, demand_scores, color='#2ca02c')
        axs[0, 1].set_title('Demand Score (1-10)')
        axs[0, 1].tick_params(axis='x', rotation=45)
        
        # Supply subplot
        axs[1, 0].bar(formatted_crop_names, supply_scores, color='#d62728')
        axs[1, 0].set_title('Supply Score (1-10)')
        axs[1, 0].tick_params(axis='x', rotation=45)
        
        # Profit potential subplot
        axs[1, 1].bar(formatted_crop_names, profit_potentials, color='#ff7f0e')
        axs[1, 1].set_title('Profit Potential (1-10)')
        axs[1, 1].tick_params(axis='x', rotation=45)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Encode the image to base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str
    
    def explain_market_trends(self, crop_name, month, year=2023):
        """
        Generate a textual explanation of market trends.
        
        Args:
            crop_name: Name of the crop
            month: Month (1-12)
            year: Year, defaults to 2023
            
        Returns:
            String explanation of market trends
        """
        metrics = self.get_market_metrics(crop_name, month, year)
        if not metrics:
            return f"No market data available for {crop_name} in month {month}, {year}."
        
        # Get data for previous month for comparison
        prev_month = 12 if month == 1 else month - 1
        prev_year = year - 1 if month == 1 else year
        prev_metrics = self.get_market_metrics(crop_name, prev_month, prev_year)
        
        explanation_parts = []
        
        # Format crop name for display
        display_name = crop_name.replace('_', ' ').capitalize()
        
        # Current price analysis
        if metrics['price_per_kg'] > 100:
            explanation_parts.append(f"{display_name} currently has a high market price of Rs. {metrics['price_per_kg']:.2f} per kg.")
        elif metrics['price_per_kg'] > 50:
            explanation_parts.append(f"{display_name} currently has a moderate market price of Rs. {metrics['price_per_kg']:.2f} per kg.")
        else:
            explanation_parts.append(f"{display_name} currently has a relatively low market price of Rs. {metrics['price_per_kg']:.2f} per kg.")
        
        # Price trend analysis
        if prev_metrics:
            price_change = metrics['price_per_kg'] - prev_metrics['price_per_kg']
            price_change_pct = (price_change / prev_metrics['price_per_kg']) * 100
            
            if price_change_pct > 10:
                explanation_parts.append(f"The price has increased significantly by {price_change_pct:.1f}% compared to last month.")
            elif price_change_pct > 0:
                explanation_parts.append(f"The price has slightly increased by {price_change_pct:.1f}% compared to last month.")
            elif price_change_pct > -10:
                explanation_parts.append(f"The price has slightly decreased by {abs(price_change_pct):.1f}% compared to last month.")
            else:
                explanation_parts.append(f"The price has decreased significantly by {abs(price_change_pct):.1f}% compared to last month.")
        
        # Demand analysis
        if metrics['demand_score'] >= 8:
            explanation_parts.append(f"There is very high market demand for {display_name} (score: {metrics['demand_score']}/10).")
        elif metrics['demand_score'] >= 6:
            explanation_parts.append(f"There is good market demand for {display_name} (score: {metrics['demand_score']}/10).")
        else:
            explanation_parts.append(f"The market demand for {display_name} is moderate to low (score: {metrics['demand_score']}/10).")
        
        # Supply analysis
        if metrics['supply_score'] >= 8:
            explanation_parts.append(f"The market has abundant supply of {display_name} (score: {metrics['supply_score']}/10).")
        elif metrics['supply_score'] >= 6:
            explanation_parts.append(f"The market has adequate supply of {display_name} (score: {metrics['supply_score']}/10).")
        else:
            explanation_parts.append(f"The market supply for {display_name} is limited (score: {metrics['supply_score']}/10), which may keep prices higher.")
        
        # Profit potential analysis
        if metrics['profit_potential'] >= 8:
            explanation_parts.append(f"{display_name} has excellent profit potential this season (score: {metrics['profit_potential']}/10).")
        elif metrics['profit_potential'] >= 6:
            explanation_parts.append(f"{display_name} has good profit potential this season (score: {metrics['profit_potential']}/10).")
        else:
            explanation_parts.append(f"{display_name} has moderate to low profit potential this season (score: {metrics['profit_potential']}/10).")
        
        # Add a conclusion
        if metrics['demand_score'] > metrics['supply_score'] and metrics['profit_potential'] >= 6:
            explanation_parts.append(f"Overall, market conditions favor growing {display_name} this season due to favorable demand-supply dynamics.")
        elif metrics['demand_score'] < metrics['supply_score'] and metrics['profit_potential'] < 6:
            explanation_parts.append(f"Overall, market conditions suggest caution when growing {display_name} this season due to high supply relative to demand.")
        else:
            explanation_parts.append(f"Overall, {display_name} presents a balanced market opportunity with moderate risk and returns.")
        
        return " ".join(explanation_parts)
