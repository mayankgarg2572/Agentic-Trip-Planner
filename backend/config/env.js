// /config/env.js
const path = require('path');
const dotenv = require('dotenv');

dotenv.config({ path: path.resolve(__dirname, '../.env') });

// Helper: ensure required vars exist
function requireEnv(name) {
  if (!process.env[name]) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return process.env[name];
}

module.exports = {
  port: process.env.PORT || 5000,
  allowedOrigins: process.env.ALLOWED_ORIGINS?.split(',').map(o => o.trim()),
  requireEnv
};
