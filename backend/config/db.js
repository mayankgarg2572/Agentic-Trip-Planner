const mongoose = require('mongoose');
const {requireEnv} =  require("./env")
const connectDB = async () => {
  const connURL = "mongodb+srv://"+requireEnv("MONGODB_USERNAME")+":"+requireEnv("MONGODB_USER_PASSWORD")+"@"+requireEnv("MONGODBCLUSTER")+".mongodb.net/?retryWrites=true&w=majority&appName="+requireEnv("MONGODB_APPNAME")
  try {
    await mongoose.connect(connURL, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('MongoDB connected successfully.');
  } catch (error) {
    console.error('MongoDB connection failed:', error);
    throw error
    // process.exit(1); // Exit process with failure
  }
};

module.exports = connectDB;
