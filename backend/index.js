const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const path = require('path'); // Import path module
const connectDB = require('./config/db');
const locationRoutes = require('./routes/locationRoutes');
const itineraryRoutes = require('./routes/itineraryRoutes');

// dotenv.config();
dotenv.config({ path: path.resolve(__dirname, '.env') });
const app = express();

// Middleware
app.use(express.json());

// CORS configuration clearly allowing only specified frontend URL
const corsOptions = {
  origin: 'http://localhost:3000', // clearly your frontend URL
  methods: 'GET, POST, PUT, DELETE',
  credentials: true,
};

app.use(cors(corsOptions));


// Routes
app.use('/api', locationRoutes);
app.use('/api', itineraryRoutes);

// Connect to Database and Start Server
const PORT = process.env.PORT || 5000;

connectDB().then(() => {
  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
});
