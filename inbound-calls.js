import WebSocket from "ws";
import Pusher from "pusher";

const pusher = new Pusher({
  appId: "1943029",
  key: "0e35b2b61a995822dd68",
  secret: "208b7d83b141bdff87f2",
  cluster: "us2",
  useTLS: true
});

export function registerInboundRoutes(fastify) {
  const { ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID } = process.env;

  if (!ELEVENLABS_API_KEY || !ELEVENLABS_AGENT_ID) {
    console.error("Missing required environment variables");
    throw new Error("Missing ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID");
  }

  async function getSignedUrl() {
    try {
      const response = await fetch(
        `https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id=${ELEVENLABS_AGENT_ID}`,
        {
          method: 'GET',
          headers: { 'xi-api-key': ELEVENLABS_API_KEY }
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to get signed URL: ${response.statusText}`);
      }

      const data = await response.json();
      console.info("Got signed integer");
      return data.signed_url;
    } catch (error) {
      console.error("Error getting signed URL:", error);
      throw error;
    }
  }

  fastify.all("/incoming-call-eleven", async (request, reply) => {
    const twimlResponse = `<?xml version="1.0" encoding="UTF-8"?>
      <Response>
        <Connect>
          <Stream url="wss://${request.headers.host}/media-stream" />
        </Connect>
      </Response>`;

    reply.type("text/xml").send(twimlResponse);
  });

  fastify.register(async (fastifyInstance) => {
    fastifyInstance.get("/media-stream", { websocket: true }, async (connection, req) => {
      console.info("[Server] Twilio connected to media stream.");
      pusher.trigger("calls-channel", "call-started", { message: "Incoming call started" });

      let streamSid = null;
      let elevenLabsWs = null;

      try {
        const signedUrl = await getSignedUrl();
        elevenLabsWs = new WebSocket(signedUrl);

        elevenLabsWs.on("open", () => console.log("[II] Connected to Conversational AI."));
        elevenLabsWs.on("message", (data) => {
          try {
            const message = JSON.parse(data);
            handleElevenLabsMessage(message, connection);
          } catch (error) {
            console.error("[II] Error parsing message:", error);
          }
        });
        elevenLabsWs.on("error", (error) => console.error("[II] WebSocket error:", error));
        elevenLabsWs.on("close", () => console.log("[II] Disconnected."));

        const handleElevenLabsMessage = (message, connection) => {
          switch (message.type) {
            case "audio":
              if (message.audio_event?.audio_base_64) {
                const audioData = {
                  event: "media",
                  streamSid,
                  media: { payload: message.audio_event.audio_base_64 },
                };
                pusher.trigger("calls-channel", "audio-received", {
                  message: "New audio data received",
                  data: audioData
                });
                connection.send(JSON.stringify(audioData));
              }
              break;
          }
        };

        connection.on("message", async (message) => {
          try {
            const data = JSON.parse(message);
            streamSid = data.streamSid;
            switch (data.event) {
              case "start":
                console.log(`[Twilio] Stream started with ID: ${streamSid}`);
                pusher.trigger("calls-channel", "call-initiated", {
                  message: `Call initiated with stream ID: ${streamSid}`
                });
                break;
              case "stop":
                if (elevenLabsWs) elevenLabsWs.close();
                console.log("[Twilio] Call ended");
                pusher.trigger("calls-channel", "call-ended", {
                  message: "Call has ended"
                });
                break;
            }
          } catch (error) {
            console.error("[Twilio] Error processing message:", error);
          }
        });

        connection.on("close", () => {
          if (elevenLabsWs) elevenLabsWs.close();
          console.log("[Twilio] Client disconnected");
          pusher.trigger("calls-channel", "call-disconnected", {
            message: "Call disconnected"
          });
        });

      } catch (error) {
        console.error("[Server] Error initializing conversation:", error);
        if (elevenLabsWs) elevenLabsWs.close();
        connection.socket.close();
      }
    });
  });
}
