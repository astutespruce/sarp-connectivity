import React, { useEffect } from "react"

import Intro from "./Intro"
import UseCases from "./UseCases"
import ScoringOverview from "./ScoringOverview"
import SARP from "./SARP"
import Credits from "./Credits"

// import NetworkConnectivity from "./priorities/NetworkConnectivity"
// import WatershedCondition from "./priorities/WatershedCondition"
// import Combined from "./priorities/Combined"

import fishImage from "../../../img/iStock-181890680.jpg"

// From SARP
import demolitionImage from "../../../img/Steeles_Mill_Dam_Hitchcock_Creek_during_removal__Peter_Raabe_A.jpg"

// From: TNC and also https://www.americanrivers.org/2018/05/fish-swim-free-in-roaring-river-tennessee/
import roaringRiverDamImage from "../../../img/Roaring_River_dam_removal_-_All_the_Partners_-_DSC_0178.jpg"

// Photo from: https://www.flickr.com/photos/usfwssoutheast/33643110826/in/album-72157675681441135/
// import CaneRiverDam from "../../../img/33643110826_a90387d592_z.jpg"

import { scrollIntoView } from "../../../utils/dom"

const Home = () => {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })

    return (
        <div id="ContentPage">
            <div className="image-header" style={{ backgroundImage: `url(${fishImage})` }} />

            <div className="container">
                <Intro />
                <UseCases />
            </div>

            <div className="image-divider" style={{ backgroundImage: `url(${roaringRiverDamImage})` }}>
                <div className="credits">
                    Roaring River Dam Removal, Tennessee, 2017. Mark Thurman, Tennessee Wildlife Resources Agency.
                </div>
            </div>

            <div className="container">
                <ScoringOverview />
            </div>

            <div className="image-divider" style={{ backgroundImage: `url(${demolitionImage})` }}>
                <div className="credits">
                    Steeles Mill Dam Hitchcock Creek during removal. Photo credit: Peter Raabe, American Rivers.
                </div>
            </div>

            <div className="container">
                <SARP />

                <Credits />
            </div>
        </div>
    )
}

export default Home
