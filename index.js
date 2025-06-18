import Fastify from "fastify";
import dotenv from "dotenv";
import fastifyFormBody from "@fastify/formbody";
import fastifyWs from "@fastify/websocket";
import { registerInboundRoutes } from './inbound-calls.js';

// Load environment variables from .env file
dotenv.config();

// Initialize Fastify server
const fastify = Fastify({
  logger: true // Enable logging
});

fastify.register(fastifyFormBody);
fastify.register(fastifyWs);

const PORT = process.env.PORT || 8000;

// Root route for health check
fastify.get("/", async (_, reply) => {
  reply.send({ message: "Financial Call Answer System is running" });
});

// Start the Fastify server
const start = async () => {
  try {
    // Register route handlers
    await registerInboundRoutes(fastify);

    // Start listening
    await fastify.listen({ port: PORT, host: '0.0.0.0' });
    console.log(`[Server] Financial Call Answer System listening on port ${PORT}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('Unhandled rejection:', err);
  process.exit(1);
});

start();