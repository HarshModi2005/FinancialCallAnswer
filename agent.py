import requests
import os

# Load API key securely from environment variables
ELEVENLABS_API_KEY = "sk_0520cc9cadbba16670ec7525304c16614bf2f030bd52424d"

# Ensure the API key is available
if not ELEVENLABS_API_KEY:
    raise ValueError("API Key is missing. Set ELEVENLABS_API_KEY as an environment variable.")

def create_agent():
    response = requests.post(
        "https://api.elevenlabs.io/v1/convai/agents/create",  # Corrected API endpoint
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "name": "Stock Price Assistant",
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": "You are a financial assistant using Gemini to provide real-time stock data and market analysis. Your capabilities include fetching stock prices, historical trends, market summaries, and related news.",
                        "llm": "gemini-1.5-pro",
                        "temperature": 0.7,
                        "max_tokens": 512,
                        "tools": [
                            {
                                "type": "webhook",
                                "name": "get_stock_price",
                                "description": "Fetches real-time stock prices and company details.",
                                "api_schema": {
                                    "url": "https://query2.finance.yahoo.com/v7/finance/quote",
                                    "method": "GET",
                                    "query_params_schema": {
                                        "properties": {
                                            "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL)"}
                                        },
                                        "required": ["symbol"]
                                    }
                                }
                            },
                            {
                                "type": "webhook",
                                "name": "get_stock_history",
                                "description": "Retrieves historical stock data for analysis.",
                                "api_schema": {
                                    "url": "https://query1.finance.yahoo.com/v8/finance/chart/",
                                    "method": "GET",
                                    "query_params_schema": {
                                        "properties": {
                                            "symbol": {"type": "string", "description": "Stock symbol"},
                                            "period": {"type": "string", "description": "Time period (1d, 5d, 1mo, etc.)"}
                                        },
                                        "required": ["symbol", "period"]
                                    }
                                }
                            },
                            {
                                "type": "webhook",
                                "name": "get_market_summary",
                                "description": "Provides a summary of major market indices.",
                                "api_schema": {
                                    "url": "https://finance.yahoo.com/",
                                    "method": "GET"
                                }
                            },
                            {
                                "type": "webhook",
                                "name": "search_news",
                                "description": "Finds recent news and analysis for stocks.",
                                "api_schema": {
                                    "url": "https://www.alphavantage.co/query",
                                    "method": "GET",
                                    "query_params_schema": {
                                        "properties": {
                                            "query": {"type": "string", "description": "Search term"},
                                            "num_results": {"type": "integer", "description": "Number of results (1-10)"}
                                        },
                                        "required": ["query"]
                                    }
                                }
                            }
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
