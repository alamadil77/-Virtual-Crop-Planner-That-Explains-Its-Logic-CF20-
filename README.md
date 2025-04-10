# -Virtual-Crop-Planner-That-Explains-Its-Logic-CF20-
Virtual Crop Planner is an intelligent decision-support system that helps farmers and agricultural planners choose the most suitable crops to grow based on soil type, climate conditions, water availability, crop rotation practices, and market demand.


Hey, this HTML page is super easy to use and shows off Smart Crop Advisor, which suggests crops based on soil and season.  It's got a header with links, a cool tagline, a form to enter soil type and season, and info on common crops.  The JavaScript makes it work – you pick soil and season, click "Get Crop Suggestion," and boom, you get a recommendation with an explanation. It looks great too, all soft green and works perfectly on phones.



In this web page more features are added to make it more user interactive and user friendly. Price chart together with image of the crop is also added as new features. Core functionality is implemented using JavaScript; upon user selection of soil type and season, clicking "Get Crop Suggestion" generates a crop recommendation with supporting rationale. And an API is added to fetch the market price of the crop. The static HTML table shows example price changes for a few crops from Jan to Apr: Each crop has an image stored and is used to display a relevant image with the crop recommendation.


In this HTML file , new features are added and for better prediction and more clarification in data few more data inputs are added. Designed to assist users (especially farmers) in choosing the most suitable crop based on inputs like soil type, season, temperature, and rainfall. It also integrates live weather detection, animated UI, and a Chart.js-based market price visualization. An intro screen is also added to make is more user interactive.A simple table showing price changes for a few crops, used to give users an example of market volatility.



Virtual crop planner.  A data driven crop planning platform that suggests what to grow based on current market trends,health of soil and season and its logic . In this CSS and HTML is used for frontend and python is used at backend. The ML is based on random forest model. The detail analysis for each recommendation of crop is given. And the platform is user friendly and interactive. For every recommendation a detailed and pictorial chart are prepared for better understanding.



The provided Python code defines a `DataProcessor' class that serves as a smart crop advisory engine by analyzing both soil and market conditions to recommend the most suitable crops for a given planting month. It loads crop requirements and market trends from CSV files, maps months to agricultural seasons, and filters crops accordingly. The system evaluates soil compatibility based on nutrient levels (nitrogen, phosphorus, potassium), pH, temperature, humidity, and rainfall, assigning weighted scores to reflect suitability. Simultaneously, it calculates a market score using crop-specific data like price, demand, supply, and profit potential, also with weighted importance. These scores are then combined (60% soil, 40% market) to generate an overall score for each crop. Finally, the class ranks and returns the top crop recommendations that are both agronomically and economically viable, making it a practical tool for precision agriculture and informed farming decisions.



The `ExplanationGenerator' class is a modular system designed to generate personalized crop-growing advice based on soil quality, market trends, and seasonal suitability. It analyzes soil parameters (like nitrogen, phosphorus, pH, etc.) to explain compatibility, evaluates market conditions using scores and optional metrics (like price, demand, and supply), and assesses the seasonal timing by matching the crop’s growing season with the current month. It can generate individual explanations, a full recommendation report for a single crop, or compare multiple crops based on their combined scores. The outputs are clear, human-readable summaries ideal for integrating into a smart farming app or advisory platform.



Crop Data: Information about growing requirements for various crops
Market Data: Current and historical market trends, prices, and demand factors
Usage
Adjust the soil parameters using the sliders in the sidebar
Set the month and optional environmental parameters
Click "Get Crop Recommendations" to generate personalized suggestions
Explore the detailed analysis for each recommended crop

Installation
Unzip the smart_crop_planner.zip file
Install the required dependencies:
pip install streamlit pandas numpy matplotlib plotly scikit-learn nltk joblib
Run the application:
streamlit run app.py
