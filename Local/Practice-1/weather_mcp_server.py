"""
Weather FastMCP server example.
Run with:
    uv run server weather_fastmcp_server stdio
"""
import requests
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("WeatherServer")

# Add weather tool
@mcp.tool()
def get_weather(location: str) -> dict:
    """Get current weather for any location"""
    try:
        response = requests.get(f"http://wttr.in/{location}?format=j1", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            
            return {
                'location': f"{data['nearest_area'][0]['areaName'][0]['value']}, {data['nearest_area'][0]['country'][0]['value']}",
                'temperature': f"{current['temp_C']}°C ({current['temp_F']}°F)",
                'condition': current['weatherDesc'][0]['value'],
                'humidity': f"{current['humidity']}%",
                'wind': f"{current['windspeedKmph']} km/h",
                'feels_like': f"{current['FeelsLikeC']}°C ({current['FeelsLikeF']}°F)"
            }
        else:
            return {"error": f"Could not get weather for {location}"}
            
    except Exception as e:
        return {"error": str(e)}

# Add weather forecast tool
@mcp.tool()
def get_forecast(location: str, days: int = 3) -> dict:
    """Get weather forecast for a location (up to 3 days)"""
    try:
        response = requests.get(f"http://wttr.in/{location}?format=j1", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            forecast = []
            
            # Get forecast for requested days (max 3)
            for i in range(min(days, len(data['weather']))):
                day_data = data['weather'][i]
                forecast.append({
                    'date': day_data['date'],
                    'max_temp': f"{day_data['maxtempC']}°C ({day_data['maxtempF']}°F)",
                    'min_temp': f"{day_data['mintempC']}°C ({day_data['mintempF']}°F)",
                    'condition': day_data['hourly'][0]['weatherDesc'][0]['value'],
                    'chance_of_rain': f"{day_data['hourly'][0]['chanceofrain']}%"
                })
            
            return {
                'location': f"{data['nearest_area'][0]['areaName'][0]['value']}, {data['nearest_area'][0]['country'][0]['value']}",
                'forecast': forecast
            }
        else:
            return {"error": f"Could not get forecast for {location}"}
            
    except Exception as e:
        return {"error": str(e)}

# Add dynamic weather resource
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

# Add weather analysis prompt
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

# Add weather comparison prompt
@mcp.prompt()
def compare_weather(location1: str, location2: str) -> str:
    """Generate a prompt to compare weather between two locations"""
    return f"""Compare the current weather conditions between {location1} and {location2}. 
    Analyze the differences in temperature, humidity, wind, and overall conditions. 
    Provide insights about which location has more favorable weather and for what activities."""

if __name__ == "__main__":
    mcp.run(transport="sse")