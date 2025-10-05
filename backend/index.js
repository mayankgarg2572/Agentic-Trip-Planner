const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const path = require('path'); // Import path module
const connectDB = require('./config/db');
const locationRoutes = require('./routes/locationRoutes');


dotenv.config({ path: path.resolve(__dirname, '.env') });
const app = express();

app.use(express.json());


const corsOptions = {
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  methods: 'GET, POST, PUT, DELETE',
  credentials: true,
};

app.use(cors(corsOptions));


// Routes
app.use('/api', locationRoutes);

// Connect to Database and Start Server
const PORT = process.env.PORT || 5000;

connectDB().then(() => {
  console.log("db for search backend is enabled")
})
.catch((err)=>{
  console.log("Error in connecting to DB in search Backend:", err)
})

;

app.listen(PORT, () => {
    console.log(`Search Backend Server is running on port ${PORT}`);
  });
