import React from "react"

import Section from "../Section"

import { ReactComponent as HighLandcoverIcon } from "../../../../img/nat_landcover_high.svg"
import { ReactComponent as LowLandcoverIcon } from "../../../../img/nat_landcover_low.svg"

function NaturalLandcover() {
    return (
        <Section id="NaturalLandcoverDef" title="Floodplain Natural Landcover">
            <p>
                Rivers and streams that have a greater amount of natural landcover in their floodplain are more likely
                to have higher quality aquatic habitat. These areas may have more cool-water refugia for temperature
                sensitive species due to shading from the overstory, and may have fewer water quality issues. In
                contrast, rivers that have less natural landcover are more likely to be altered and have impaired water
                quality.
            </p>
            <div className="prioritization-details flex-container flex-justify-space-between">
                <div>
                    <HighLandcoverIcon />
                    <h4 className="is-size-4 text-align-center">High Natural Landcover</h4>
                    <p>
                        Barriers with aquatic networks that have more natural landcover are more likely to contribute
                        higher quality habitat if they are removed.
                    </p>
                </div>
                <div>
                    <LowLandcoverIcon />
                    <h4 className="is-size-4 text-align-center">Low Natural Landcover</h4>
                    <p>
                        Barriers with less natural landcover are less likely to contribute high quality habitat for
                        aquatic species if removed.
                    </p>
                </div>
            </div>
            <h5 className="title is-5">Methods:</h5>
            <ol>
                <li>Floodplains are delineated using: TODO: floodplain methods from Kat</li>
                <li>Natural landcover is derived from ... TODO: methods from Kat... </li>
                <li>Natural landcover is clipped to the floodplain area for analysis</li>
                <li>
                    The contributing watershed (catchment) of each stream and river reach is extracted from the NHDPlus
                    dataset
                </li>
                <li>
                    The total amount of area in natural landcover and total floodplain area are tallied for each
                    functional network
                </li>
                <li>
                    Floodplain natural landcover is measured from the overall percent of natural landcover throughout
                    the entire functional network
                </li>
            </ol>
        </Section>
    )
}

export default NaturalLandcover
