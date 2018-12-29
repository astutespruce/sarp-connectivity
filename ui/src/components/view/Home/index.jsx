import React, { useEffect } from "react"

import Intro from "./Intro"
import Inventory from "./Inventory"
import UseCases from "./UseCases"
import Concepts from "./Concepts"
import SARP from "./SARP"
import Credits from "./Credits"

// import NetworkConnectivity from "./priorities/NetworkConnectivity"
// import WatershedCondition from "./priorities/WatershedCondition"
// import Combined from "./priorities/Combined"

import damImage from "../../../img/american-public-power-association-430861-unsplash.jpg"

// From SARP
import demolitionImage from "../../../img/Steeles_Mill_Dam_Hitchcock_Creek_during_removal__Peter_Raabe_A.jpg"

import { scrollIntoView } from "../../../utils/dom"

const Home = () => {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })

    return (
        <div id="ContentPage" className="view">
            <Intro />

            <div className="image-divider" style={{ backgroundImage: `url(${damImage})` }}>
                <div className="credits">
                    Photo credit:{" "}
                    <a href="https://unsplash.com/photos/FUeb2npsblQ" target="_blank" rel="noopener noreferrer">
                        American Public Power Association
                    </a>
                </div>
            </div>

            {/* <UseCases /> */}

            <Concepts />

            <div className="image-divider" style={{ backgroundImage: `url(${demolitionImage})` }}>
                <div className="credits">
                    Steeles Mill Dam Hitchcock Creek during removal. Photo credit: Peter Raabe.
                </div>
            </div>

            <SARP />

            <Credits />
        </div>
    )
}

export default Home
