"""
EVI Quick Response Tools
Fast, user-facing tools that EVI can use directly
"""

import os
import logging
import requests
from datetime import datetime
import pytz
from typing import Dict, Any

class EVITools:
    """Collection of quick response tools for EVI"""

    def __init__(self):
        self.logger = logging.getLogger('pattern3.tools')
        self.logger.debug("Initializing EVITools")
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        
    def get_weather(self, location: str, units: str = "fahrenheit") -> str:
        """
        Get current weather for a location.

        Args:
            location: City name (e.g., "New York" or "London,UK")
            units: "fahrenheit" or "celsius"

        Returns:
            Weather description string
        """
        self.logger.info(f"Getting weather for {location} ({units})")
        try:
            # Use OpenWeatherMap API (free tier)
            # Sign up at: https://openweathermap.org/api

            if not self.weather_api_key:
                self.logger.warning("Weather API key not configured")
                return "Weather service is not configured. Please set OPENWEATHER_API_KEY."

            # Determine units for API
            api_units = "imperial" if units == "fahrenheit" else "metric"
            unit_symbol = "°F" if units == "fahrenheit" else "°C"

            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": self.weather_api_key,
                "units": api_units
            }

            self.logger.debug(f"Calling weather API for {location}")
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']

                self.logger.info(f"Weather retrieved: {location} - {temp:.0f}{unit_symbol}, {description}")
                return (f"The weather in {location} is {description} with a temperature "
                       f"of {temp:.0f}{unit_symbol}, feels like {feels_like:.0f}{unit_symbol}. "
                       f"Humidity is {humidity}%.")
            elif response.status_code == 404:
                self.logger.warning(f"Location not found: {location}")
                return f"Sorry, I couldn't find weather information for {location}."
            else:
                self.logger.warning(f"Weather API returned status {response.status_code}")
                return "Weather service is temporarily unavailable."

        except Exception as e:
            self.logger.error(f"Weather API error: {e}", exc_info=True)
            print(f"Weather API error: {e}")
            return "I'm having trouble getting the weather right now."
    
    def get_time(self, timezone: str = "America/New_York") -> str:
        """
        Get current time in a specific timezone.

        Args:
            timezone: Timezone string (e.g., "America/New_York", "Europe/London")

        Returns:
            Current time string
        """
        self.logger.info(f"Getting time for timezone: {timezone}")
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            formatted_time = current_time.strftime("%I:%M %p")
            formatted_date = current_time.strftime("%A, %B %d, %Y")

            self.logger.debug(f"Time retrieved: {formatted_time} on {formatted_date}")
            return f"The current time in {timezone} is {formatted_time} on {formatted_date}."

        except pytz.exceptions.UnknownTimeZoneError:
            self.logger.warning(f"Unknown timezone: {timezone}")
            return f"Sorry, I don't recognize the timezone '{timezone}'."
        except Exception as e:
            self.logger.error(f"Time error: {e}", exc_info=True)
            print(f"Time error: {e}")
            return "I'm having trouble getting the time right now."
    
    def calculate(self, expression: str) -> str:
        """
        Perform simple calculations safely.

        Args:
            expression: Math expression (e.g., "15 * 23")

        Returns:
            Calculation result
        """
        self.logger.info(f"Calculating expression: {expression}")
        try:
            # Sanitize input - only allow numbers and basic operators
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                self.logger.warning(f"Invalid characters in expression: {expression}")
                return "I can only calculate expressions with numbers and basic operators (+, -, *, /)."

            # Safely evaluate
            result = eval(expression)
            self.logger.info(f"Calculation result: {expression} = {result}")
            return f"The answer is {result}."

        except ZeroDivisionError:
            self.logger.warning("Division by zero attempted")
            return "I can't divide by zero."
        except Exception as e:
            self.logger.error(f"Calculation error: {e}", exc_info=True)
            print(f"Calculation error: {e}")
            return "I couldn't calculate that expression."
    
    def confirm_action(self, action: str, details: str = "") -> str:
        """
        Ask user to confirm an action before proceeding.
        This is a conversational tool - EVI will speak this.

        Args:
            action: The action to confirm
            details: Additional details about the action

        Returns:
            Confirmation prompt
        """
        self.logger.info(f"Requesting confirmation for action: {action}")
        prompt = f"Just to confirm, you'd like me to {action}"
        if details:
            prompt += f". {details}"
        prompt += ". Is that correct? Please say yes or no."

        self.logger.debug(f"Confirmation prompt: {prompt}")
        return prompt


# Tool definitions for Hume EVI Platform
# These need to be created in the Hume platform UI or via API

EVI_TOOL_DEFINITIONS = [
    {
        "name": "get_weather",
        "description": "Get current weather information for any location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, optionally with country code (e.g., 'New York' or 'London,UK')"
                },
                "units": {
                    "type": "string",
                    "enum": ["fahrenheit", "celsius"],
                    "description": "Temperature units"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_time",
        "description": "Get current time in any timezone",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')"
                }
            },
            "required": []
        }
    },
    {
        "name": "calculate",
        "description": "Perform simple mathematical calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g., '15 * 23', '100 / 4')"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "confirm_action",
        "description": "Ask user to confirm an action before proceeding",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to be confirmed"
                },
                "details": {
                    "type": "string",
                    "description": "Additional details about the action"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "consult_crew",
        "description": "Route complex queries to specialized AI agents for research, analysis, and comprehensive responses. Use this when the query requires: multi-step reasoning, current research, detailed analysis, comparing multiple options, or expert knowledge beyond quick facts.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The complex query to be processed by specialized agents"
                },
                "context": {
                    "type": "string",
                    "description": "Optional additional context about what the user is trying to accomplish"
                }
            },
            "required": ["query"]
        }
    }
]


if __name__ == "__main__":
    # Test the tools
    tools = EVITools()
    
    print("=== Testing EVI Quick Tools ===\n")
    
    # Test weather (will fail without API key, but shows structure)
    print("Weather Test:")
    print(tools.get_weather("New York"))
    print()
    
    # Test time
    print("Time Test:")
    print(tools.get_time("America/Los_Angeles"))
    print()
    
    # Test calculator
    print("Calculator Test:")
    print(tools.calculate("15 * 23"))
    print()
    
    # Test confirmation
    print("Confirmation Test:")
    print(tools.confirm_action("schedule a meeting", "Tomorrow at 2 PM"))