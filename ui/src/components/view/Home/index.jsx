import React, { useEffect } from "react"

import Intro from "./Intro"
import Tool from "./Tool"
import Inventory from "./Inventory"
import UseCases from "./UseCases"
import Concepts from "./Concepts"
import ScoringOverview from "./ScoringOverview"
import SARP from "./SARP"
import Credits from "./Credits"

// import NetworkConnectivity from "./priorities/NetworkConnectivity"
// import WatershedCondition from "./priorities/WatershedCondition"
// import Combined from "./priorities/Combined"

// import DamImage from "../../../img/american-public-power-association-430861-unsplash.jpg"

import { scrollIntoView } from "../../../utils/dom"

const Home = () => {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })

    return (
        <div id="ContentPage" className="view">
            <Intro />

            <Tool />

            {/* <div className="image-divider" style={{ backgroundImage: `url(${DamImage})` }} /> */}

            <Inventory />

            <UseCases />

            <Concepts />

            <ScoringOverview />
            {/* 
            <NetworkLength />

            <NetworkComplexity />

            <NetworkSinuosity />

            <NaturalLandcover />

            <NetworkConnectivity />

            <WatershedCondition />

            <Combined /> */}

            <SARP />

            <Credits />
        </div>
    )
}

export default Home
