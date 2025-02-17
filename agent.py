import requests

# Load API key securely
ELEVENLABS_API_KEY = "sk_0520cc9cadbba16670ec7525304c16614bf2f030bd52424d"  # Replace with your actual API key
ALPHA_VANTAGE_API_KEY = "5PBGETDT1CIC2MY1"  # Replace with your actual Alpha Vantage API key

# Ensure the API key is available
if not ELEVENLABS_API_KEY or not ALPHA_VANTAGE_API_KEY:
    raise ValueError("API Key is missing. Set ELEVENLABS_API_KEY and ALPHA_VANTAGE_API_KEY.")

def create_stock_price_agent():
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
                        "prompt": "You provide real-time stock prices and news using Alpha Vantage API.",
                        "llm": "gemini-1.5-pro",
                        "temperature": 0.7,
                        "max_tokens": 512,
                        "tools": [
                            {
                                "type": "webhook",
                                "name": "get_stock_price",
                                "description": "Fetches real-time stock prices.",
                                "api_schema": {
                                    "url": "https://www.alphavantage.co/query",
                                    "method": "GET",
                                    "query_params_schema": {
                                        "properties": {
                                            "function": {"type": "string", "description": "API function (TIME_SERIES_INTRADAY, TIME_SERIES_DAILY, etc.)"},
                                            "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL)"},
                                            "apikey": {"type": "string", "description": "Alpha Vantage API key", "default": ALPHA_VANTAGE_API_KEY}
                                        },
                                        "required": ["function", "symbol", "apikey"]
                                    },
                                    "fixed_query_params": {
                                        "apikey": ALPHA_VANTAGE_API_KEY
                                    }
                                }
                            },
                            {
                                "type": "webhook",
                                "name": "get_stock_news",
                                "description": "Fetches stock-related news.",
                                "api_schema": {
                                    "url": "https://www.alphavantage.co/query",
                                    "method": "GET",
                                    "query_params_schema": {
                                        "properties": {
                                            "function": {"type": "string", "description": "API function (NEWS_SENTIMENT)"},
                                            "tickers": {"type": "string", "description": "Comma-separated stock symbols"},
                                            "topics": {"type": "string", "description": "Comma-separated news topics"},
                                            "limit": {"type": "integer", "description": "Number of news items to return"},
                                            "apikey": {"type": "string", "description": "Alpha Vantage API key", "default": ALPHA_VANTAGE_API_KEY}
                                        },
                                        "required": ["function", "apikey"]
                                    },
                                    "fixed_query_params": {
                                        "function": "NEWS_SENTIMENT",
                                        "apikey": ALPHA_VANTAGE_API_KEY
                                    }
                                }
                            }
                        ]
                    },
                    "first_message": "Hi! I can fetch real-time stock prices and news. What stock symbol do you need?",
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
print(create_stock_price_agent())
