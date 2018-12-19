import React, { useEffect } from "react"

import Intro from "./Intro"
import Tool from "./Tool"
import Inventory from "./Inventory"
import UseCases from "./UseCases"
import Concepts from "./Concepts"
import ScoringOverview from "./ScoringOverview"
import SARP from "./SARP"
import Credits from "./Credits"

import NetworkLength from "./metrics/NetworkLength"
import NetworkSinuosity from "./metrics/NetworkSinuosity"
import NetworkComplexity from "./metrics/NetworkComplexity"
import NaturalLandcover from "./metrics/NaturalLandcover"

import NetworkConnectivity from "./priorities/NetworkConnectivity"
import WatershedCondition from "./priorities/WatershedCondition"
import Combined from "./priorities/Combined"

import { scrollIntoView } from "../../../utils/dom"

const Home = () => {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })

    return (
        <div id="ContentPage" className="view">
            <Intro />

            <Tool />

            <Inventory />

            <UseCases />

            <Concepts />

            <ScoringOverview />

            <NetworkLength />

            <NetworkComplexity />

            <NetworkSinuosity />

            <NaturalLandcover />

            <NetworkConnectivity />

            <WatershedCondition />

            <Combined />

            <SARP />

            <Credits />
        </div>
    )
}

export default Home
