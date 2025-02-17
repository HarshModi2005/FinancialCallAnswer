import WebSocket from "ws";

export function registerInboundRoutes(fastify) {
  const { ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID } = process.env;
  if (!ELEVENLABS_API_KEY || !ELEVENLABS_AGENT_ID) {
    console.error("[Error] Missing required environment variables");
    throw new Error("Missing ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID");
  }

  async function getSignedUrl() {
    try {
      console.info("[Info] Fetching signed URL from ElevenLabs API...");
      const response = await fetch(
        `https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id=${ELEVENLABS_AGENT_ID}`,
        { headers: { 'xi-api-key': ELEVENLABS_API_KEY } }
      );
      if (!response.ok) throw new Error(`Failed to get signed URL: ${response.statusText}`);
      console.info("[Success] Retrieved signed URL.");
      return (await response.json()).signed_url;
    } catch (error) {
      console.error("[Error] Error getting signed URL:", error);
      throw error;
    }
  }

  fastify.all("/incoming-call-eleven", async (request, reply) => {
    console.info("[Incoming] Received call event from Twilio.");
    reply.type("text/xml").send(`<?xml version="1.0" encoding="UTF-8"?>
      <Response>
        <Connect>
          <Stream url="wss://${request.headers.host}/media-stream" />
        </Connect>
      </Response>`);
  });

  fastify.register(async (fastifyInstance) => {
    fastifyInstance.get("/media-stream", { websocket: true }, async (connection, req) => {
      console.info("[Server] Twilio connected to media stream.");
      let streamSid = null;
      let elevenLabsWs = null;

      try {
        console.info("[Info] Establishing WebSocket connection with ElevenLabs...");
        elevenLabsWs = new WebSocket(await getSignedUrl());
        elevenLabsWs.on("open", () => console.log("[Success] Connected to ElevenLabs AI."));
        elevenLabsWs.on("message", (data) => handleElevenLabsMessage(JSON.parse(data), connection));
        elevenLabsWs.on("error", (error) => console.error("[Error] ElevenLabs WebSocket error:", error));
        elevenLabsWs.on("close", () => console.log("[Info] ElevenLabs WebSocket disconnected."));

        function handleElevenLabsMessage(message, connection) {
          console.log("[Message Received]", message);
          switch (message.type) {
            case "conversation_initiation_metadata":
              console.info("[Info] Received conversation initiation metadata from ElevenLabs.");
              break;
            case "audio":
              if (message.audio_event?.audio_base_64) {
                console.info("[Info] Forwarding audio event to Twilio.");
                connection.send(JSON.stringify({
                  event: "media", streamSid,
                  media: { payload: message.audio_event.audio_base_64 },
                }));
              }
              break;
            case "interruption":
              console.warn("[Warning] Interruption event received, clearing stream.");
              connection.send(JSON.stringify({ event: "clear", streamSid }));
              break;
            case "ping":
              console.info("[Ping] Received ping event, sending pong response.");
              if (message.ping_event?.event_id) {
                elevenLabsWs.send(JSON.stringify({ type: "pong", event_id: message.ping_event.event_id }));
              }
              break;
          }
        }

        connection.on("message", async (message) => {
          try {
            const data = JSON.parse(message);
            streamSid = data.streamSid;
            switch (data.event) {
              case "start":
                console.info(`[Twilio] Stream started with ID: ${streamSid}`);
                break;
              case "media":
                console.info("[Twilio] Received media event, forwarding to ElevenLabs.");
                if (elevenLabsWs?.readyState === WebSocket.OPEN) {
                  elevenLabsWs.send(JSON.stringify({
                    user_audio_chunk: Buffer.from(data.media.payload, "base64").toString("base64"),
                  }));
                }
                break;
              case "stop":
                console.info("[Twilio] Stream stopped, closing ElevenLabs connection.");
                elevenLabsWs?.close();
                break;
              default:
                console.warn(`[Twilio] Unhandled event received: ${data.event}`);
            }
          } catch (error) {
            console.error("[Twilio] Error processing message:", error);
          }
        });

        connection.on("close", () => {
          console.info("[Twilio] Client disconnected, closing ElevenLabs WebSocket.");
          elevenLabsWs?.close();
        });

        connection.on("error", (error) => {
          console.error("[Twilio] WebSocket error:", error);
          elevenLabsWs?.close();
        });
      } catch (error) {
        console.error("[Server] Error initializing conversation:", error);
        elevenLabsWs?.close();
        connection.socket.close();
      }
    });
  });
}
