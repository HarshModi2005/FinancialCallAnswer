import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Ensure the API keys are available
if not ELEVENLABS_API_KEY:
    raise ValueError("ElevenLabs API Key is missing. Set ELEVENLABS_API_KEY in your environment variables.")
if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("Alpha Vantage API Key is missing. Set ALPHA_VANTAGE_API_KEY in your environment variables.")

def create_agent():
    response = requests.post(
        "https://api.elevenlabs.io/v1/convai/agents/create",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "name": "Stock Price Assistant",
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": "You are a financial assistant using Alpha Vantage to provide real-time stock data and market analysis...",
                        "llm": "gemini-1.5-pro",
                        "temperature": 0.7,
                        "max_tokens": 512,
                        "tools": [
                            {
                                "type": "webhook",
                                "name": "get_stock_price",
                                "description": "Fetches real-time stock prices and company details.",
                                "api_schema": {
                                    "url": "https://www.alphavantage.co/query",
                                    "method": "GET",
                                    "query_params_schema": {
                                        "properties": {
                                            "function": {
                                                "type": "string",
                                                "description": "The API function to call.",
                                                "enum": ["GLOBAL_QUOTE"]
                                            },
                                            "symbol": {
                                                "type": "string",
                                                "description": "Stock symbol (e.g., AAPL)"
                                            },
                                            "apikey": {
                                                "type": "string",
                                                "description": "Your Alpha Vantage API key",
                                                "default": ALPHA_VANTAGE_API_KEY
                                            }
                                        },
                                        "required": ["function", "symbol", "apikey"]
                                    }
                                }
                            },
                            # Additional tools can be defined here
                        ]
                    },
                    "first_message": "Hi! I can provide real-time stock prices, historical trends, and market analysis. What do you need help with?",
                    "language": "en"
                },
                "asr": {
                    "quality": "high",
                    "provider": "elevenlabs",
                    "user_input_audio_format": "ulaw_8000",
                    "keywords": []
                },
                "tts": {
                    "model_id": "eleven_turbo_v2",
                    "voice_id": "cjVigY5qzO86Huf0OWal",
                    "agent_output_audio_format": "ulaw_8000",
                    "optimize_streaming_latency": 3,
                    "stability": 0.5,
                    "similarity_boost": 0.8
                }
            }
        },
    )
    
    return response.json()

# Call the function and print the response
print(create_agent())
