import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import base64
from io import BytesIO

# Import custom modules
from data_processor import DataProcessor
from crop_recommendation_model import CropRecommendationModel
from market_trend_analyzer import MarketTrendAnalyzer
from explanation_generator import ExplanationGenerator

# Set page configuration
st.set_page_config(
    page_title="Smart Crop Planner",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'soil_params' not in st.session_state:
    st.session_state.soil_params = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_crop' not in st.session_state:
    st.session_state.selected_crop = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = False

# Initialize the components
@st.cache_resource
def load_data_processor():
    return DataProcessor()

@st.cache_resource
def load_crop_model():
    model = CropRecommendationModel()
    # Train the model on first load
    model.train_model()
    return model

@st.cache_resource
def load_market_analyzer():
    return MarketTrendAnalyzer()

@st.cache_resource
def load_explanation_generator():
    return ExplanationGenerator()

data_processor = load_data_processor()
crop_model = load_crop_model()
market_analyzer = load_market_analyzer()
explanation_generator = load_explanation_generator()

# Helper functions
def get_current_month():
    return datetime.now().month

def format_crop_name(name):
    return name.replace('_', ' ').title()

# App title and introduction
st.title("🌱 Smart Crop Planning Platform")
st.markdown("""
This platform helps you make data-driven decisions about what crops to grow based on your soil conditions, 
current market trends, and seasonal factors. All recommendations come with clear explanations.
""")

# Sidebar for input parameters
st.sidebar.header("Input Parameters")

# Get current month (default to current month)
current_month = get_current_month()
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month = st.sidebar.slider("Month", 1, 12, current_month)
st.sidebar.caption(f"Selected month: {month_names[month-1]}")

# Soil parameters input
st.sidebar.subheader("Soil Parameters")

soil_n = st.sidebar.slider("Nitrogen (N) kg/ha", 0, 200, 80, 5)
soil_p = st.sidebar.slider("Phosphorus (P) kg/ha", 0, 150, 50, 5)
soil_k = st.sidebar.slider("Potassium (K) kg/ha", 0, 200, 60, 5)
soil_ph = st.sidebar.slider("pH Level", 3.0, 9.0, 6.5, 0.1)

# Optional parameters
st.sidebar.subheader("Environmental Parameters (Optional)")
show_advanced = st.sidebar.checkbox("Show Advanced Parameters")

if show_advanced:
    temperature = st.sidebar.slider("Temperature (°C)", 5, 45, 25, 1)
    humidity = st.sidebar.slider("Humidity (%)", 10, 100, 60, 5)
    rainfall = st.sidebar.slider("Rainfall (mm/month)", 0, 300, 100, 10)
    
    # Create soil parameters dictionary with all inputs
    soil_params = {
        'nitrogen': soil_n,
        'phosphorus': soil_p,
        'potassium': soil_k,
        'ph': soil_ph,
        'temperature': temperature,
        'humidity': humidity,
        'rainfall': rainfall,
        'month': month
    }
else:
    # Create soil parameters dictionary with basic inputs
    soil_params = {
        'nitrogen': soil_n,
        'phosphorus': soil_p,
        'potassium': soil_k,
        'ph': soil_ph,
        'month': month
    }

# Button to get recommendations
if st.sidebar.button("Get Crop Recommendations"):
    st.session_state.soil_params = soil_params
    
    # Get recommendations from both methods
    ml_recommendations = crop_model.predict(soil_params)
    rule_recommendations = data_processor.get_top_recommendations(soil_params, month)
    
    # Combine the recommendations
    combined_recommendations = []
    
    # Process ML model recommendations
    for crop_name, probability in ml_recommendations[:10]:  # Get top 10 from ML
        # Find if this crop is also in rule-based recommendations
        rule_rec = next((r for r in rule_recommendations if r['crop_name'] == crop_name), None)
        
        if rule_rec:
            # Average the scores if found in both
            combined_score = (probability + rule_rec['combined_score']) / 2
            soil_score = rule_rec['soil_score']
            market_score = rule_rec['market_score']
        else:
            # Use ML probability if not found in rule-based
            combined_score = probability
            soil_score = 0.5  # Default values
            market_score = 0.5
        
        # Get crop details from data processor
        crop_details = data_processor.crop_data[data_processor.crop_data['crop_name'] == crop_name]
        if not crop_details.empty:
            season = crop_details.iloc[0]['season']
            growing_days = crop_details.iloc[0]['growing_days']
        else:
            season = "unknown"
            growing_days = 0
        
        combined_recommendations.append({
            'crop_name': crop_name,
            'combined_score': combined_score,
            'soil_score': soil_score,
            'market_score': market_score,
            'season': season,
            'growing_days': growing_days
        })
    
    # Add any remaining rule-based recommendations not already included
    for rule_rec in rule_recommendations:
        if not any(r['crop_name'] == rule_rec['crop_name'] for r in combined_recommendations):
            combined_recommendations.append(rule_rec)
    
    # Sort by combined score
    combined_recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # Store in session state
    st.session_state.recommendations = combined_recommendations[:10]  # Top 10 recommendations
    
    # Add to history with timestamp
    history_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'soil_params': soil_params.copy(),
        'top_recommendations': [rec['crop_name'] for rec in combined_recommendations[:3]]
    }
    st.session_state.history.append(history_entry)

# Main content area
if st.session_state.soil_params:
    # Display NPK gauge chart
    st.header("Soil Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.soil_params['nitrogen'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Nitrogen (N) kg/ha"},
            gauge={
                'axis': {'range': [0, 200]},
                'bar': {'color': "#38761d"},
                'steps': [
                    {'range': [0, 50], 'color': "#e6f2ff"},
                    {'range': [50, 100], 'color': "#99ccff"},
                    {'range': [100, 200], 'color': "#4d94ff"}
                ]
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.soil_params['phosphorus'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Phosphorus (P) kg/ha"},
            gauge={
                'axis': {'range': [0, 150]},
                'bar': {'color': "#b45f06"},
                'steps': [
                    {'range': [0, 30], 'color': "#ffe6cc"},
                    {'range': [30, 60], 'color': "#ffcc99"},
                    {'range': [60, 150], 'color': "#ff9933"}
                ]
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.soil_params['potassium'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Potassium (K) kg/ha"},
            gauge={
                'axis': {'range': [0, 200]},
                'bar': {'color': "#674ea7"},
                'steps': [
                    {'range': [0, 50], 'color': "#e6e6ff"},
                    {'range': [50, 100], 'color': "#b3b3ff"},
                    {'range': [100, 200], 'color': "#6666ff"}
                ]
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.soil_params['ph'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "pH Level"},
            gauge={
                'axis': {'range': [3, 9]},
                'bar': {'color': "#a61c00"},
                'steps': [
                    {'range': [3, 5.5], 'color': "#ffe6e6"},  # Acidic
                    {'range': [5.5, 7.5], 'color': "#99ff99"},  # Neutral
                    {'range': [7.5, 9], 'color': "#ffcc99"}   # Alkaline
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 2},
                    'thickness': 0.75,
                    'value': 6.5  # Optimal pH for many crops
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # Display the current season based on month
    season_mapping = {
        1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Fall", 10: "Fall", 11: "Fall",
        12: "Winter"
    }
    current_season = season_mapping[month]
    
    st.info(f"Current season based on selected month: **{current_season}** (Month: {month})")
    
    # Display recommendations
    if st.session_state.recommendations:
        st.header("Crop Recommendations")
        
        # Create a selection box for the crops
        crop_options = [f"{format_crop_name(rec['crop_name'])} ({rec['combined_score']*100:.1f}%)" 
                       for rec in st.session_state.recommendations]
        
        selected_option = st.selectbox("Select a crop for detailed analysis:", crop_options)
        
        # Extract the crop name from the selected option
        selected_crop_name = selected_option.split(" (")[0].lower().replace(" ", "_")
        st.session_state.selected_crop = selected_crop_name
        
        # Display the top recommendations as cards in a grid
        st.subheader("Top Recommended Crops")
        
        # Display the top 5 recommendations in a grid
        cols = st.columns(5)
        for i, rec in enumerate(st.session_state.recommendations[:5]):
            with cols[i]:
                crop_name = format_crop_name(rec['crop_name'])
                score = rec['combined_score'] * 100
                
                # Choose a color based on the score
                if score >= 75:
                    color = "#4CAF50"  # Green
                elif score >= 60:
                    color = "#FFC107"  # Amber
                else:
                    color = "#FF9800"  # Orange
                
                # Create a card-like display
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; border: 1px solid {color}; margin-bottom: 10px;">
                    <h3 style="color: {color}; margin: 0 0 10px 0;">{crop_name}</h3>
                    <p><strong>Score:</strong> {score:.1f}%</p>
                    <p><strong>Season:</strong> {rec['season'].capitalize()}</p>
                    <p><strong>Growing days:</strong> {rec['growing_days']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Display a bar chart comparing the top 10 recommendations
        st.subheader("Comparison of Top Recommendations")
        
        # Prepare data for the bar chart
        chart_data = pd.DataFrame({
            'Crop': [format_crop_name(rec['crop_name']) for rec in st.session_state.recommendations[:10]],
            'Soil Compatibility': [rec['soil_score'] * 100 for rec in st.session_state.recommendations[:10]],
            'Market Potential': [rec['market_score'] * 100 for rec in st.session_state.recommendations[:10]],
            'Overall Score': [rec['combined_score'] * 100 for rec in st.session_state.recommendations[:10]]
        })
        
        # Create the bar chart
        fig = px.bar(chart_data, x='Crop', y=['Soil Compatibility', 'Market Potential', 'Overall Score'],
                    title="Comparison of Top Recommended Crops",
                    labels={'value': 'Score (%)', 'variable': 'Category'},
                    color_discrete_map={
                        'Soil Compatibility': '#4c78a8',
                        'Market Potential': '#f58518',
                        'Overall Score': '#72b7b2'
                    })
        fig.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # If a crop is selected, show detailed analysis
        if st.session_state.selected_crop:
            selected_crop = next((rec for rec in st.session_state.recommendations 
                                if rec['crop_name'] == st.session_state.selected_crop), None)
            
            if selected_crop:
                st.header(f"Detailed Analysis: {format_crop_name(selected_crop['crop_name'])}")
                
                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(["Recommendation", "Market Analysis", "Growth Requirements", "Explanation"])
                
                with tab1:
                    # Get the crop details from the data
                    crop_details = data_processor.crop_data[data_processor.crop_data['crop_name'] == selected_crop['crop_name']]
                    
                    if not crop_details.empty:
                        crop_detail = crop_details.iloc[0]
                        
                        # Create two columns for the layout
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.subheader("Crop Information")
                            st.markdown(f"""
                            - **Name:** {format_crop_name(selected_crop['crop_name'])}
                            - **Season:** {crop_detail['season'].capitalize()}
                            - **Growing Days:** {crop_detail['growing_days']} days
                            - **Overall Score:** {selected_crop['combined_score']*100:.1f}%
                            - **Soil Compatibility:** {selected_crop['soil_score']*100:.1f}%
                            - **Market Potential:** {selected_crop['market_score']*100:.1f}%
                            """)
                        
                        with col2:
                            # Get market data for the crop
                            market_data = market_analyzer.get_market_metrics(
                                selected_crop['crop_name'], 
                                st.session_state.soil_params['month']
                            )
                            
                            if market_data:
                                st.subheader("Current Market Information")
                                st.markdown(f"""
                                - **Current Price:** Rs. {market_data['price_per_kg']:.2f} per kg
                                - **Demand:** {market_data['demand_score']}/10
                                - **Supply:** {market_data['supply_score']}/10
                                - **Profit Potential:** {market_data['profit_potential']}/10
                                """)
                            else:
                                st.warning("Market data not available for this crop.")
                    
                    # Generate and display the explanation
                    st.subheader("Recommendation Explanation")
                    
                    # Get market data for explanation
                    market_data = market_analyzer.get_market_metrics(
                        selected_crop['crop_name'], 
                        st.session_state.soil_params['month']
                    )
                    
                    # Generate the explanation
                    explanation = explanation_generator.generate_comprehensive_explanation(
                        selected_crop,
                        st.session_state.soil_params,
                        market_data,
                        st.session_state.soil_params['month']
                    )
                    
                    st.markdown(explanation)
                
                with tab2:
                    st.subheader("Market Trend Analysis")
                    
                    # Generate price chart for the selected crop
                    price_chart = market_analyzer.generate_price_chart(selected_crop['crop_name'])
                    
                    if price_chart:
                        st.image(f"data:image/png;base64,{price_chart}", caption=f"Price Trend for {format_crop_name(selected_crop['crop_name'])}")
                    else:
                        st.warning("Price trend data not available for this crop.")
                    
                    # Get detailed market explanation
                    market_explanation = market_analyzer.explain_market_trends(
                        selected_crop['crop_name'],
                        st.session_state.soil_params['month']
                    )
                    
                    st.subheader("Market Analysis Explanation")
                    st.write(market_explanation)
                    
                    # Compare with other top crops
                    st.subheader("Market Comparison with Other Top Crops")
                    
                    # Get top 5 crop names
                    top_crops = [rec['crop_name'] for rec in st.session_state.recommendations[:5]]
                    
                    # Generate comparison chart
                    comparison_chart = market_analyzer.generate_market_comparison(
                        top_crops,
                        st.session_state.soil_params['month']
                    )
                    
                    if comparison_chart:
                        st.image(f"data:image/png;base64,{comparison_chart}", 
                                caption="Market Comparison of Top Recommended Crops")
                    else:
                        st.warning("Comparison data not available.")
                
                with tab3:
                    st.subheader("Optimal Growing Conditions")
                    
                    # Get the crop details from the data
                    crop_details = data_processor.crop_data[data_processor.crop_data['crop_name'] == selected_crop['crop_name']]
                    
                    if not crop_details.empty:
                        crop_detail = crop_details.iloc[0]
                        
                        # Display optimal soil parameters
                        st.markdown("### Soil Requirements")
                        
                        # Create a comparison table of optimal vs. current values
                        comparison_data = {
                            'Parameter': ['Nitrogen (kg/ha)', 'Phosphorus (kg/ha)', 'Potassium (kg/ha)', 'pH'],
                            'Optimal Value': [
                                f"{crop_detail['nitrogen_requirement']}",
                                f"{crop_detail['phosphorus_requirement']}",
                                f"{crop_detail['potassium_requirement']}",
                                f"{crop_detail['ph_min']} - {crop_detail['ph_max']}"
                            ],
                            'Your Soil': [
                                f"{st.session_state.soil_params['nitrogen']}",
                                f"{st.session_state.soil_params['phosphorus']}",
                                f"{st.session_state.soil_params['potassium']}",
                                f"{st.session_state.soil_params['ph']}"
                            ]
                        }
                        
                        # Convert to DataFrame and display
                        comparison_df = pd.DataFrame(comparison_data)
                        st.table(comparison_df)
                        
                        # Display optimal climate parameters
                        st.markdown("### Climate Requirements")
                        
                        climate_data = {
                            'Parameter': ['Temperature (°C)', 'Humidity (%)', 'Rainfall (mm/month)'],
                            'Optimal Range': [
                                f"{crop_detail['temperature_min']} - {crop_detail['temperature_max']}",
                                f"{crop_detail['humidity_min']} - {crop_detail['humidity_max']}",
                                f"{crop_detail['rainfall_min']} - {crop_detail['rainfall_max']}"
                            ]
                        }
                        
                        # Add current values if available
                        if 'temperature' in st.session_state.soil_params:
                            climate_data['Current Value'] = [
                                f"{st.session_state.soil_params['temperature']}",
                                f"{st.session_state.soil_params['humidity']}",
                                f"{st.session_state.soil_params['rainfall']}"
                            ]
                        
                        # Convert to DataFrame and display
                        climate_df = pd.DataFrame(climate_data)
                        st.table(climate_df)
                        
                        # Add growing season information
                        st.markdown("### Growing Season")
                        
                        if crop_detail['season'] == 'kharif':
                            season_info = "Kharif season (June to October) - Monsoon crop"
                        elif crop_detail['season'] == 'rabi':
                            season_info = "Rabi season (October to March) - Winter crop"
                        elif crop_detail['season'] == 'summer':
                            season_info = "Summer season (March to June) - Summer crop"
                        else:  # annual
                            season_info = "Annual crop - Can be grown year-round with proper management"
                        
                        st.info(season_info)
                        
                        # Add growing days information
                        st.markdown("### Growing Timeline")
                        st.write(f"This crop typically takes **{crop_detail['growing_days']} days** from planting to harvest.")
                        
                        # Calculate estimated harvest date
                        current_date = datetime.now()
                        harvest_date = current_date + pd.Timedelta(days=int(crop_detail['growing_days']))
                        
                        st.write(f"If planted today, estimated harvest would be around: **{harvest_date.strftime('%B %d, %Y')}**")
                    else:
                        st.warning("Detailed growing information not available for this crop.")
                
                with tab4:
                    st.subheader("Detailed Explanation")
                    
                    # Get feature importance from the ML model
                    feature_importance = crop_model.get_feature_importance()
                    
                    # Create a bar chart of feature importance
                    importance_df = pd.DataFrame({
                        'Feature': list(feature_importance.keys()),
                        'Importance': list(feature_importance.values())
                    })
                    importance_df = importance_df.sort_values('Importance', ascending=False)
                    
                    st.markdown("### Factors that influence crop selection")
                    
                    fig = px.bar(importance_df, x='Importance', y='Feature', orientation='h',
                                title="Importance of different factors in crop selection",
                                color='Importance',
                                color_continuous_scale=px.colors.sequential.Viridis)
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig)
                    
                    # Generate model explanation for this prediction
                    model_explanation = crop_model.explain_prediction(
                        st.session_state.soil_params, 
                        selected_crop['crop_name']
                    )
                    
                    st.markdown("### Why this crop is recommended")
                    st.write(model_explanation)
                    
                    # Get explanation from the explanation generator
                    explanation = explanation_generator.generate_comprehensive_explanation(
                        selected_crop,
                        st.session_state.soil_params,
                        market_analyzer.get_market_metrics(
                            selected_crop['crop_name'], 
                            st.session_state.soil_params['month']
                        ),
                        st.session_state.soil_params['month']
                    )
                    
                    st.markdown("### Comprehensive Analysis")
                    st.markdown(explanation)
        
        # Display history of recommendations
        if st.session_state.history:
            with st.expander("View Recommendation History"):
                st.subheader("Previous Recommendations")
                
                for i, entry in enumerate(reversed(st.session_state.history), 1):
                    st.markdown(f"""
                    **{entry['timestamp']}**  
                    Soil: N={entry['soil_params']['nitrogen']}, P={entry['soil_params']['phosphorus']}, K={entry['soil_params']['potassium']}, pH={entry['soil_params']['ph']}  
                    Top crops: {', '.join([format_crop_name(crop) for crop in entry['top_recommendations']])}
                    """)
                    st.markdown("---")
else:
    # Display a welcome message if no recommendations have been generated yet
    st.info("👈 Please enter your soil parameters in the sidebar and click 'Get Crop Recommendations' to start.")

    # Display a sample analysis section
    st.header("What You'll Get")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🌱 Crop Recommendations")
        st.markdown("""
        - Top crop suggestions based on your inputs
        - Ranked by overall compatibility
        - Tailored to your specific soil conditions
        """)
    
    with col2:
        st.markdown("### 📊 Market Analysis")
        st.markdown("""
        - Current market prices and trends
        - Demand and supply insights
        - Profit potential assessment
        """)
    
    with col3:
        st.markdown("### 📝 Clear Explanations")
        st.markdown("""
        - Plain language descriptions of why each crop is recommended
        - Detailed soil compatibility analysis
        - Seasonal planting guidance
        """)
    
    # Display how it works section
    st.header("How It Works")
    
    st.image("https://miro.medium.com/max/1400/1*9V6tVh8aFJEWQlLYQAn0JA.png", 
             caption="Illustration of machine learning for agriculture (Source: Medium)")
    
    st.markdown("""
    Our platform combines several advanced technologies:
    1. **Machine Learning Models**: Analyze soil parameters to find the most suitable crops
    2. **Data Analytics**: Evaluate current market trends and prices
    3. **Agricultural Science**: Apply crop-specific knowledge about growing conditions
    4. **Natural Language Processing**: Generate easy-to-understand explanations
    
    By integrating these technologies, we provide recommendations that balance 
    agronomic suitability with market opportunity.
    """)
    
    # Call to action
    st.success("Enter your soil parameters in the sidebar to get started!")

# Footer
st.markdown("---")
st.markdown("Smart Crop Planner © 2023 | Powered by agricultural data and machine learning")
