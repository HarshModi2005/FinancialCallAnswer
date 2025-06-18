# Financial Call Answer System

An AI-powered financial call answering system that integrates Twilio for phone calls with ElevenLabs AI for intelligent conversation handling.

## Features

- **Inbound Call Handling**: Receives and processes inbound phone calls via Twilio webhooks
- **Real-time Audio Streaming**: Bidirectional audio streaming between Twilio and ElevenLabs AI
- **AI-Powered Conversations**: Uses ElevenLabs conversational AI for natural phone interactions
- **WebSocket Integration**: Real-time communication using WebSocket connections
- **Health Check Endpoint**: Built-in health monitoring

## Architecture

```
Caller → Twilio → Your Server → ElevenLabs AI
                      ↓
                 WebSocket Stream
                      ↓
              Real-time Audio Processing
```

## Setup

### Prerequisites

- Node.js (v18 or higher)
- Twilio account with phone number
- ElevenLabs account with conversational AI agent

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   
4. Configure your `.env` file with:
   - `ELEVENLABS_API_KEY`: Your ElevenLabs API key
   - `ELEVENLABS_AGENT_ID`: Your ElevenLabs conversational agent ID
   - `PORT`: Server port (optional, defaults to 8000)

### Running the Application

```bash
npm start
```

The server will start on `http://localhost:8000` (or your configured PORT).

## Configuration

### Twilio Setup

1. Configure your Twilio phone number webhook URL to point to:
   ```
   https://your-domain.com/incoming-call-eleven
   ```

2. Ensure your server is publicly accessible (use ngrok for local development):
   ```bash
   npx ngrok http 8000
   ```

### ElevenLabs Setup

1. Create a conversational AI agent in your ElevenLabs dashboard
2. Note the Agent ID for your `.env` configuration
3. Ensure your API key has appropriate permissions

## API Endpoints

- `GET /` - Health check endpoint
- `POST/GET /incoming-call-eleven` - Twilio webhook for incoming calls
- `WebSocket /media-stream` - Media streaming endpoint for real-time audio

## Development

The application uses:
- **Fastify** - Fast and efficient web framework
- **WebSocket** - Real-time bidirectional communication
- **ElevenLabs API** - AI-powered conversation handling
- **Twilio** - Phone call management

## Logging

The application provides detailed logging for:
- Incoming call events
- WebSocket connection status
- Audio streaming events
- Error handling and debugging

## Security Notes

- Never commit your `.env` file to version control
- Use HTTPS in production
- Validate webhook signatures in production (recommended Twilio security practice)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

ISC 