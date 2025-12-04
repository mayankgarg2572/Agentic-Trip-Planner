import React, { useState, useEffect } from "react";
import HomeDesktop from "./HomeDesktop";
import HomeMobile from "./HomeMobile";
import api from "../api/api";
const Home = () => {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    window.addEventListener("resize", handleResize);

    const verifyBackendServices = async () => {
        try {
        await api.startServer();
      } catch (error) {
        console.error(error);
      }
      }
      verifyBackendServices()
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return isMobile ? <HomeMobile /> : <HomeDesktop />;
};

export default Home;
