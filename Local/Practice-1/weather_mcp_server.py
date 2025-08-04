"""
Weather FastMCP server example with improved error handling.
Run with:
    python weather_server.py
"""
import requests
import logging
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("WeatherServer")

@mcp.tool()
def get_weather(location: str) -> dict:
    """Get current weather for any location"""
    logger.info(f"Getting weather for: {location}")
    
    try:
        # Add more specific location formatting
        formatted_location = location.replace(" ", "+")
        url = f"http://wttr.in/{formatted_location}?format=j1"
        logger.info(f"Requesting: {url}")
        
        response = requests.get(url, timeout=15)
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we have the expected data structure
            if 'current_condition' not in data or not data['current_condition']:
                logger.error("No current condition data in response")
                return {"error": f"No weather data available for {location}"}
            
            current = data['current_condition'][0]
            
            # Handle cases where nearest_area might be missing
            location_name = location
            if 'nearest_area' in data and data['nearest_area']:
                area = data['nearest_area'][0]
                location_name = f"{area['areaName'][0]['value']}, {area['country'][0]['value']}"
            
            result = {
                'location': location_name,
                'temperature': f"{current['temp_C']}°C ({current['temp_F']}°F)",
                'condition': current['weatherDesc'][0]['value'],
                'humidity': f"{current['humidity']}%",
                'wind': f"{current['windspeedKmph']} km/h",
                'feels_like': f"{current['FeelsLikeC']}°C ({current['FeelsLikeF']}°F)"
            }
            
            logger.info(f"Weather data retrieved successfully: {result}")
            return result
        else:
            error_msg = f"Weather service returned status {response.status_code} for {location}"
            logger.error(error_msg)
            return {"error": error_msg}
            
    except requests.RequestException as e:
        error_msg = f"Network error getting weather for {location}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    except (KeyError, IndexError) as e:
        error_msg = f"Error parsing weather data for {location}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error getting weather for {location}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def get_forecast(location: str, days: int = 3) -> dict:
    """Get weather forecast for a location (up to 3 days)"""
    logger.info(f"Getting forecast for: {location}, days: {days}")
    
    try:
        formatted_location = location.replace(" ", "+")
        url = f"http://wttr.in/{formatted_location}?format=j1"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'weather' not in data or not data['weather']:
                return {"error": f"No forecast data available for {location}"}
            
            forecast = []
            
            for i in range(min(days, len(data['weather']))):
                day_data = data['weather'][i]
                forecast.append({
                    'date': day_data['date'],
                    'max_temp': f"{day_data['maxtempC']}°C ({day_data['maxtempF']}°F)",
                    'min_temp': f"{day_data['mintempC']}°C ({day_data['mintempF']}°F)",
                    'condition': day_data['hourly'][0]['weatherDesc'][0]['value'],
                    'chance_of_rain': f"{day_data['hourly'][0]['chanceofrain']}%"
                })
            
            location_name = location
            if 'nearest_area' in data and data['nearest_area']:
                area = data['nearest_area'][0]
                location_name = f"{area['areaName'][0]['value']}, {area['country'][0]['value']}"
            
            result = {
                'location': location_name,
                'forecast': forecast
            }
            
            logger.info(f"Forecast data retrieved successfully")
            return result
        else:
            error_msg = f"Weather service returned status {response.status_code} for {location}"
            logger.error(error_msg)
            return {"error": error_msg}
            
    except Exception as e:
        error_msg = f"Error getting forecast for {location}: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.resource("weather://{location}")
def get_weather_resource(location: str) -> str:
    """Get weather data as a resource"""
    weather_data = get_weather(location)
    
    if 'error' in weather_data:
        return f"Error: {weather_data['error']}"
    
    return f"""Weather Report for {weather_data['location']}

Current Conditions:
- Temperature: {weather_data['temperature']} (feels like {weather_data['feels_like']})
- Condition: {weather_data['condition']}
- Humidity: {weather_data['humidity']}
- Wind Speed: {weather_data['wind']}
"""

@mcp.prompt()
def weather_analysis(location: str, context: str = "general") -> str:
    """Generate a weather analysis prompt"""
    contexts = {
        "travel": "Analyze the weather conditions for travel planning",
        "outdoor": "Analyze the weather for outdoor activities", 
        "clothing": "Suggest appropriate clothing based on weather",
        "general": "Provide a general weather analysis"
    }
    
    prompt_context = contexts.get(context, contexts['general'])
    
    return f"""Based on the current weather data for {location}, please {prompt_context.lower()}. 
Consider temperature, humidity, wind conditions, and any weather advisories. 
Provide practical advice and recommendations."""

if __name__ == "__main__":
    logger.info("Starting Weather MCP Server...")
    mcp.run(transport="streamable-http")