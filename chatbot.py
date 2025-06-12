import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env variables if using locally
load_dotenv()

# Initialize the OpenAI client using your API key
client = OpenAI(base_url="https://models.github.ai/inference",
                api_key=os.getenv("OPENAI_o1_MINI_API_KEY"))  # or GITHUB_TOKEN if used

def get_aqi_advice(forecasted_aqi, user_health_issues=None, current_aqi=None, city=None):
    """
    Get AQI-based health advice using OpenAI API
    
    Args:
        forecasted_aqi: List of forecasted AQI values
        user_health_issues: User's health concerns or questions (optional)
        current_aqi: Current AQI value (optional)
        city: City name (optional)
    
    Returns:
        str: Health advice and recommendations
    """
    
    system_prompt = (
        "You are an expert air quality health advisor that provides practical, evidence-based advice "
        "based on Air Quality Index (AQI) levels. Use guidelines from WHO, CDC, EPA, and CPCB. "
        "Provide clear, actionable recommendations for protecting health during different air quality conditions. "
        "Be supportive and informative when users share health concerns. "
        "Keep responses concise but comprehensive, focusing on practical steps people can take."
    )

    # Build context-aware user prompt
    user_prompt = ""
    
    # Add location context if available
    if city:
        user_prompt += f"Location: {city}\n"
    
    # Add current AQI if available
    if current_aqi is not None:
        user_prompt += f"Current AQI: {current_aqi:.1f}\n"
    
    # Add forecast data
    if forecasted_aqi:
        avg_forecast = sum(forecasted_aqi) / len(forecasted_aqi)
        max_forecast = max(forecasted_aqi)
        min_forecast = min(forecasted_aqi)
        user_prompt += f"7-day AQI forecast - Average: {avg_forecast:.1f}, Range: {min_forecast:.1f} to {max_forecast:.1f}\n"
    
    # Add user's question or health concerns
    if user_health_issues:
        # Check if this is a general question or specific health concern
        health_keywords = ['asthma', 'copd', 'heart', 'lung', 'breathing', 'respiratory', 'allergy', 'pregnant', 'elderly', 'child']
        is_health_concern = any(keyword in user_health_issues.lower() for keyword in health_keywords)
        
        if is_health_concern:
            user_prompt += f"User health concern/condition: {user_health_issues}\n"
            user_prompt += "Please provide specific advice for someone with these health considerations."
        else:
            user_prompt += f"User question: {user_health_issues}\n"
            user_prompt += "Please answer their question in the context of the air quality data provided."
    else:
        user_prompt += "Please provide general health recommendations based on these air quality conditions."

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        # Fallback response if API fails
        fallback_advice = generate_fallback_advice(current_aqi, forecasted_aqi)
        return f"I'm having trouble connecting to the AI service right now. Here's some basic advice:\n\n{fallback_advice}"

def generate_fallback_advice(current_aqi=None, forecasted_aqi=None):
    """
    Generate basic AQI advice without API call as fallback
    """
    if current_aqi is None and forecasted_aqi:
        current_aqi = forecasted_aqi[-1]  # Use latest forecast value
    
    if current_aqi is None:
        return "Please ensure you have valid AQI data to get personalized advice."
    
    if current_aqi <= 50:
        return (
            "🟢 **Good Air Quality (0-50)**\n"
            "• Air quality is satisfactory\n"
            "• Outdoor activities are safe for everyone\n"
            "• Great time for exercise and outdoor recreation"
        )
    elif current_aqi <= 100:
        return (
            "🟡 **Moderate Air Quality (51-100)**\n"
            "• Air quality is acceptable for most people\n"
            "• Sensitive individuals may experience minor issues\n"
            "• Consider reducing prolonged outdoor exertion if sensitive"
        )
    elif current_aqi <= 150:
        return (
            "🟠 **Unhealthy for Sensitive Groups (101-150)**\n"
            "• People with respiratory/heart conditions should limit outdoor activities\n"
            "• Consider wearing masks when outdoors\n"
            "• Keep windows closed and use air purifiers indoors"
        )
    elif current_aqi <= 200:
        return (
            "🔴 **Unhealthy Air Quality (151-200)**\n"
            "• Everyone should limit outdoor activities\n"
            "• Wear N95 masks when going outside\n"
            "• Stay indoors with air purification when possible\n"
            "• Avoid outdoor exercise"
        )
    else:
        return (
            "🟣 **Very Unhealthy Air Quality (200+)**\n"
            "• Avoid outdoor activities entirely\n"
            "• Stay indoors with sealed windows\n"
            "• Use air purifiers and wear masks even indoors if needed\n"
            "• Seek medical attention if experiencing breathing difficulties"
        )

def get_aqi_category(aqi_value):
    """Get AQI category and color for display"""
    if aqi_value <= 50:
        return "Good", "green"
    elif aqi_value <= 100:
        return "Moderate", "yellow"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups", "orange"
    elif aqi_value <= 200:
        return "Unhealthy", "red"
    else:
        return "Very Unhealthy", "purple"