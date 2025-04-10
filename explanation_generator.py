import nltk
from nltk.tokenize import word_tokenize
import random

class ExplanationGenerator:
    def __init__(self):
        """Initialize the explanation generator."""
        # Download necessary NLTK resources if needed
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def generate_soil_explanation(self, crop_name, soil_params, soil_score):
        """
        Generate an explanation about soil compatibility.
        
        Args:
            crop_name: Name of the crop
            soil_params: Dict of soil parameters
            soil_score: Compatibility score (0-1)
            
        Returns:
            String explanation
        """
        # Format crop name for display
        display_name = crop_name.replace('_', ' ').capitalize()
        
        if soil_score >= 0.8:
            quality = "excellent"
            advice = "Your soil is very well-suited for this crop."
        elif soil_score >= 0.6:
            quality = "good"
            advice = "Your soil is suitable for this crop with minor adjustments."
        elif soil_score >= 0.4:
            quality = "moderate"
            advice = "Your soil can support this crop, but may need some amendments."
        else:
            quality = "poor"
            advice = "Your soil will need significant amendments to support this crop well."
        
        # Generate specific explanations for each soil parameter
        param_explanations = []
        
        # Nitrogen explanation
        if 'nitrogen' in soil_params:
            if soil_params['nitrogen'] < 50:
                param_explanations.append(f"The nitrogen level ({soil_params['nitrogen']}) is on the lower side. Consider adding nitrogen-rich fertilizers like urea or composted manure.")
            elif soil_params['nitrogen'] < 100:
                param_explanations.append(f"The nitrogen level ({soil_params['nitrogen']}) is adequate for many crops including {display_name}.")
            else:
                param_explanations.append(f"The nitrogen level ({soil_params['nitrogen']}) is quite high, which is beneficial for leafy crops but may cause excessive vegetative growth in some plants.")
        
        # Phosphorus explanation
        if 'phosphorus' in soil_params:
            if soil_params['phosphorus'] < 30:
                param_explanations.append(f"The phosphorus level ({soil_params['phosphorus']}) is relatively low. Consider adding bone meal or rock phosphate to enhance flowering and root development.")
            elif soil_params['phosphorus'] < 60:
                param_explanations.append(f"The phosphorus level ({soil_params['phosphorus']}) is sufficient for most crops including {display_name}.")
            else:
                param_explanations.append(f"The phosphorus level ({soil_params['phosphorus']}) is high, which generally supports good root development and flowering.")
        
        # Potassium explanation
        if 'potassium' in soil_params:
            if soil_params['potassium'] < 30:
                param_explanations.append(f"The potassium level ({soil_params['potassium']}) is on the lower side. Wood ash or potassium sulfate can increase levels to improve crop resilience.")
            elif soil_params['potassium'] < 80:
                param_explanations.append(f"The potassium level ({soil_params['potassium']}) is adequate for strong plant development and disease resistance.")
            else:
                param_explanations.append(f"The potassium level ({soil_params['potassium']}) is high, which helps with water regulation and overall crop quality.")
        
        # pH explanation
        if 'ph' in soil_params:
            if soil_params['ph'] < 5.5:
                param_explanations.append(f"The soil pH ({soil_params['ph']}) is acidic. Most crops prefer a slightly acidic to neutral pH. Consider adding lime to raise the pH.")
            elif soil_params['ph'] < 7.0:
                param_explanations.append(f"The soil pH ({soil_params['ph']}) is slightly acidic to neutral, which is ideal for most crops including {display_name}.")
            elif soil_params['ph'] < 8.0:
                param_explanations.append(f"The soil pH ({soil_params['ph']}) is slightly alkaline. Many crops can still grow well, but monitor for nutrient availability.")
            else:
                param_explanations.append(f"The soil pH ({soil_params['ph']}) is alkaline. Consider adding sulfur or organic matter to lower the pH for better nutrient absorption.")
        
        # Put it all together
        base_explanation = f"Your soil has {quality} compatibility with {display_name}. {advice}"
        
        # Choose 2-3 parameter explanations randomly if there are more than 3
        if len(param_explanations) > 3:
            selected_explanations = random.sample(param_explanations, 3)
        else:
            selected_explanations = param_explanations
        
        full_explanation = base_explanation + " " + " ".join(selected_explanations)
        
        return full_explanation
    
    def generate_market_explanation(self, crop_name, market_score, market_data=None):
        """
        Generate an explanation about market conditions.
        
        Args:
            crop_name: Name of the crop
            market_score: Market score (0-1)
            market_data: Optional dictionary with detailed market metrics
            
        Returns:
            String explanation
        """
        # Format crop name for display
        display_name = crop_name.replace('_', ' ').capitalize()
        
        if market_score >= 0.8:
            outlook = "excellent"
            recommendation = "Current market conditions strongly favor this crop."
        elif market_score >= 0.6:
            outlook = "favorable"
            recommendation = "Market conditions are generally good for this crop."
        elif market_score >= 0.4:
            outlook = "moderate"
            recommendation = "Market conditions present a balanced opportunity with some risks."
        else:
            outlook = "challenging"
            recommendation = "Market conditions may be difficult for this crop right now."
        
        base_explanation = f"{display_name} has {outlook} market prospects. {recommendation}"
        
        # Add detailed explanation if market data is available
        if market_data:
            details = []
            
            # Price analysis
            if 'price_per_kg' in market_data:
                details.append(f"The current market price is approximately Rs. {market_data['price_per_kg']:.2f} per kg.")
            
            # Demand analysis
            if 'demand_score' in market_data:
                if market_data['demand_score'] >= 8:
                    details.append(f"Demand is very high (score: {market_data['demand_score']}/10).")
                elif market_data['demand_score'] >= 6:
                    details.append(f"Demand is good (score: {market_data['demand_score']}/10).")
                else:
                    details.append(f"Demand is moderate to low (score: {market_data['demand_score']}/10).")
            
            # Supply analysis
            if 'supply_score' in market_data:
                if market_data['supply_score'] <= 4:
                    details.append(f"Supply is limited (score: {market_data['supply_score']}/10), which may support higher prices.")
                elif market_data['supply_score'] <= 7:
                    details.append(f"Supply is moderate (score: {market_data['supply_score']}/10), creating balanced market conditions.")
                else:
                    details.append(f"Supply is abundant (score: {market_data['supply_score']}/10), which may put pressure on prices.")
            
            # Profit analysis
            if 'profit_potential' in market_data:
                if market_data['profit_potential'] >= 8:
                    details.append(f"The profit potential is excellent (score: {market_data['profit_potential']}/10).")
                elif market_data['profit_potential'] >= 6:
                    details.append(f"The profit potential is good (score: {market_data['profit_potential']}/10).")
                else:
                    details.append(f"The profit potential is moderate to low (score: {market_data['profit_potential']}/10).")
            
            detailed_explanation = base_explanation + " " + " ".join(details)
            return detailed_explanation
        
        return base_explanation
    
    def generate_seasonal_explanation(self, crop_name, season, month):
        """
        Generate an explanation about seasonal suitability.
        
        Args:
            crop_name: Name of the crop
            season: Growing season for the crop
            month: Current month (1-12)
            
        Returns:
            String explanation
        """
        # Format crop name for display
        display_name = crop_name.replace('_', ' ').capitalize()
        
        # Month to season mapping
        month_to_season = {
            1: "winter", 2: "winter",  # January, February
            3: "spring", 4: "spring", 5: "spring",  # March, April, May
            6: "summer", 7: "summer", 8: "summer",  # June, July, August
            9: "fall", 10: "fall", 11: "fall",  # September, October, November
            12: "winter"  # December
        }
        
        # Season to month mapping
        season_months = {
            'kharif': "June to September (monsoon season)",
            'rabi': "October to March (winter season)",
            'summer': "March to June (summer season)",
            'annual': "year-round with proper management"
        }
        
        current_season = month_to_season[month]
        
        if season == 'annual':
            return f"{display_name} is a year-round crop that can be grown in any season with proper care and management. It adapts well to different growing conditions throughout the year."
        
        seasonal_match = {
            ('kharif', "summer"): "excellent time",
            ('kharif', "fall"): "good time",
            ('kharif', "winter"): "challenging time",
            ('kharif', "spring"): "early but possible",
            
            ('rabi', "fall"): "excellent time",
            ('rabi', "winter"): "good time",
            ('rabi', "spring"): "late but possible",
            ('rabi', "summer"): "challenging time",
            
            ('summer', "spring"): "excellent time",
            ('summer', "summer"): "good time",
            ('summer', "fall"): "challenging time",
            ('summer', "winter"): "not recommended"
        }
        
        match_quality = seasonal_match.get((season, current_season), "moderate time")
        
        if match_quality == "excellent time":
            explanation = f"This is an {match_quality} to plant {display_name}. It is a {season} crop typically grown in {season_months[season]}, which aligns perfectly with the current {current_season} season."
        elif match_quality == "good time":
            explanation = f"This is a {match_quality} to plant {display_name}. As a {season} crop typically grown in {season_months[season]}, the current {current_season} season provides suitable conditions."
        elif match_quality == "moderate time":
            explanation = f"This is a {match_quality} to plant {display_name}. While it's a {season} crop typically grown in {season_months[season]}, it can adapt to the current {current_season} season with proper care."
        elif match_quality == "challenging time":
            explanation = f"This is a {match_quality} to plant {display_name}. It's primarily a {season} crop grown in {season_months[season]}, which doesn't align well with the current {current_season} season. Consider adjusting planting time or providing additional protection."
        else:
            explanation = f"This is {match_quality} to plant {display_name}. It's a {season} crop traditionally grown in {season_months[season]}. The current {current_season} season is not ideal for this crop."
        
        return explanation
    
    def generate_comprehensive_explanation(self, crop_data, soil_params, market_data, month):
        """
        Generate a comprehensive explanation combining soil, market, and seasonal factors.
        
        Args:
            crop_data: Dict with crop information
            soil_params: Dict with soil parameters
            market_data: Dict with market metrics
            month: Current month (1-12)
            
        Returns:
            String explanation
        """
        crop_name = crop_data['crop_name']
        
        # Individual explanations
        soil_explanation = self.generate_soil_explanation(
            crop_name, soil_params, crop_data.get('soil_score', 0.5))
        
        market_explanation = self.generate_market_explanation(
            crop_name, crop_data.get('market_score', 0.5), market_data)
        
        seasonal_explanation = self.generate_seasonal_explanation(
            crop_name, crop_data.get('season', 'annual'), month)
        
        # Overall recommendation
        combined_score = crop_data.get('combined_score', 0.5)
        
        if combined_score >= 0.8:
            recommendation = f"{crop_name.replace('_', ' ').capitalize()} is highly recommended for your current conditions."
        elif combined_score >= 0.6:
            recommendation = f"{crop_name.replace('_', ' ').capitalize()} is a good choice for your current conditions."
        elif combined_score >= 0.4:
            recommendation = f"{crop_name.replace('_', ' ').capitalize()} is a reasonable option but will require some additional management."
        else:
            recommendation = f"{crop_name.replace('_', ' ').capitalize()} may be challenging to grow under your current conditions."
        
        # Combine everything
        sections = [
            f"## Recommendation: {recommendation}",
            f"### Soil Compatibility\n{soil_explanation}",
            f"### Market Outlook\n{market_explanation}",
            f"### Seasonal Timing\n{seasonal_explanation}",
            f"### Overall Assessment\nBased on combined soil, market, and seasonal factors, this crop has a compatibility score of {combined_score:.2f} out of 1.0."
        ]
        
        return "\n\n".join(sections)
    
    def generate_comparison_explanation(self, crop_recommendations, soil_params, month):
        """
        Generate a comparative explanation for multiple crop recommendations.
        
        Args:
            crop_recommendations: List of dicts with crop recommendations
            soil_params: Dict with soil parameters
            month: Current month (1-12)
            
        Returns:
            String explanation
        """
        if not crop_recommendations:
            return "No suitable crops found for your conditions."
        
        # Sort by combined score (highest first)
        sorted_recommendations = sorted(
            crop_recommendations, 
            key=lambda x: x.get('combined_score', 0), 
            reverse=True
        )
        
        # Introduction
        intro = "Here's a comparison of the top recommended crops for your conditions:"
        
        # Individual crop explanations
        crop_sections = []
        
        for i, crop in enumerate(sorted_recommendations[:3], 1):  # Top 3 crops
            crop_name = crop['crop_name'].replace('_', ' ').capitalize()
            combined_score = crop.get('combined_score', 0) * 100  # Convert to percentage
            soil_score = crop.get('soil_score', 0) * 100
            market_score = crop.get('market_score', 0) * 100
            
            section = f"### {i}. {crop_name} (Overall: {combined_score:.0f}%)\n"
            section += f"- Soil compatibility: {soil_score:.0f}%\n"
            section += f"- Market potential: {market_score:.0f}%\n"
            
            # Add a brief explanation
            if combined_score >= 75:
                section += f"- {crop_name} is an excellent choice based on your soil conditions and current market trends.\n"
            elif combined_score >= 60:
                section += f"- {crop_name} is a good option that balances soil suitability with market potential.\n"
            else:
                section += f"- {crop_name} is a viable option but may require additional management attention.\n"
            
            crop_sections.append(section)
        
        # Conclusion
        top_crop = sorted_recommendations[0]['crop_name'].replace('_', ' ').capitalize()
        conclusion = f"Based on the analysis, **{top_crop}** emerges as the most suitable crop for your specific conditions, but any of the top recommendations would be reasonable choices depending on your preferences and resources."
        
        # Combine everything
        full_explanation = "\n\n".join([intro] + crop_sections + [conclusion])
        
        return full_explanation
