import React from "react"

import Section from "./Section"
import { scrollIntoView } from "../../../utils/dom"

// From https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/
import ForestStream from "../../../img/6882770647_60c0d68a9c_z.jpg"

// From: https://www.flickr.com/photos/usfwssoutheast/7983183705/in/album-72157631529358797/
import DamRemoval from "../../../img/7983183705_4187ce9631_z.jpg"

function ScoringOverview() {
    return (
        <Section title="How are barriers prioritized for removal?">
            <div className="columns">
                <div className="column">
                    <p>
                        In order to prioritize dams for removal, they are first characterized using metrics that
                        describe the quality and status of their functional networks:
                    </p>
                    <ul>
                        <li>
                            <a onClick={() => scrollIntoView("NetworkLengthDef")}>Network length</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("NetworkComplexityDef")}>Network complexity</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("NetworkSinuosityDef")}>Network sinuosity</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("NaturalLandcoverDef")}>Floodplain natural landcover</a>
                        </li>
                    </ul>
                </div>
                <div className="column" style={{ borderLeft: '1px solid #EEE' }}>
                    <p>
                        These metrics are then combined to create three scenarios for prioritizing barriers for removal:
                    </p>
                    <ul>
                        <li>
                            <a onClick={() => scrollIntoView("NetworkConnectivityDef")}>Network connectivity</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("WatershedConditionDef")}>Watershed condition</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("CombinedScoreDef")}>
                                Network connectivity and watershed condition
                            </a>
                        </li>
                    </ul>
                </div>
            </div>

            <div className="columns">
                <div className="column">
                    <img src={ForestStream} className="photo" alt="Loakfoma Creek at Noxubee" style={{ height: 300 }} />
                </div>
                <div className="column">
                    <img
                        src={DamRemoval}
                        alt="Dam Removal on Desnons Creek, North Carolina"
                        className="photo"
                        style={{ height: 300 }}
                    />
                </div>
            </div>
        </Section>
    )
}

export default ScoringOverview
