import React from "react";
import MapView from "../components/MapView";
import CustomSearchBar from "../components/CustomSearchBar";
import BottomSheet from "../components/BottomSheet";
import classes from "./Home.module.css";

const HomeMobile = () => {
    return (
        <div className={classes.container} style={{ flexDirection: 'column' }}>
            {/* 1. Search Bar & Map Section */}
            <div className={classes.mapSection} style={{ height: '100%' }}>
                <CustomSearchBar />
                <MapView />
            </div>

            {/* 2. Bottom Sheet */}
            <BottomSheet />
        </div>
    );
};

export default HomeMobile;
