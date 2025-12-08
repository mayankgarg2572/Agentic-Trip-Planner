import React from "react";
import MapView from "../components/MapView";
import CustomSearchBar from "../components/CustomSearchBar";
import BottomSheet from "../components/BottomSheet";
import classes from "./Home.module.css";

const HomeMobile = () => {
    return (
        <div className={classes.container}>
            <div className={classes.mapSection}>
                <CustomSearchBar />
                <MapView />
            </div>

            {/* 2. Bottom Sheet */}
            <BottomSheet />
        </div>
    );
};

export default HomeMobile;
