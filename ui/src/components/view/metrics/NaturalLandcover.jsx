import React, { useEffect } from "react"

import { scrollIntoView } from "../../../utils/dom"

import highLandcoverIcon from "../../../img/nat_landcover_high.svg"
import lowLandcoverIcon from "../../../img/nat_landcover_low.svg"

import headerImage from "../../../img/6882770647_c43a945282_o.jpg"

function NaturalLandcover() {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })

    return (
        <div id="ContentPage">
            <div className="image-header" style={{ backgroundImage: `url(${headerImage})` }}>
                <div className="credits">
                    Photo credit:{" "}
                    <a
                        href="https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Loakfoma Creek, Noxubee National Wildlife Refuge, Mississippi. U.S. Fish and Wildlife Service.
                    </a>
                </div>
            </div>

            <div className="container">
                <section className="page-header">
                    <h1 className="title is-1 is-large">Floodplain natural landcover</h1>
                    <p className="is-size-4">
                        Rivers and streams that have a greater amount of natural landcover in their floodplain are more
                        likely to have higher quality aquatic habitat. These areas may have more cool-water refugia for
                        temperature sensitive species due to shading from the overstory, and may have fewer water
                        quality issues. In contrast, rivers that have less natural landcover are more likely to be
                        altered and have impaired water quality.
                    </p>
                </section>
                <section>
                    <div className="columns">
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={highLandcoverIcon} alt="natural landcover graphic" />
                                    High natural landcover
                                </h3>
                                <p>
                                    Barriers with aquatic networks that have more natural landcover are more likely to
                                    contribute higher quality habitat if they are removed.
                                </p>
                            </div>
                        </div>
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={lowLandcoverIcon} alt="natural landcover graphic" />
                                    Low natural landcover
                                </h3>
                                <p>
                                    Barriers with less natural landcover are less likely to contribute high quality
                                    habitat for aquatic species if removed.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <h3 className="subtitle is-3">Methods:</h3>
                    <ol>
                        <li>
                            Floodplains are delineated using data derived from FATHOM Inc, which has modeled 30 by 30
                            meter 100 year floodplain boundaries. For more information visit:
                            <br />
                            <a
                                href="https://iopscience.iop.org/article/10.1088/1748-9326/aaac65/pdf"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                https://iopscience.iop.org/article/10.1088/1748-9326/aaac65/pdf
                            </a>
                        </li>
                        <li>
                            Natural landcover is derived from the USDA Cropscape 2017 30 by 30 meter landcover raster
                            dataset. For more information see:{" "}
                            <a href="https://www.nass.usda.gov/" target="_blank" rel="noopener noreferrer">
                                https://www.nass.usda.gov
                            </a>
                            .
                        </li>
                        <li>
                            Natural landcover is extracted from the overall Cropscape dataset and clipped to the
                            floodplain area for analysis.
                        </li>
                        <li>
                            The contributing watershed (catchment) of each stream and river reach is extracted from the
                            NHDPlus dataset.
                        </li>
                        <li>
                            The total amount of natural landcover within the catchment area as well as the floodplain
                            area of that catchment area are tallied for each functional network.
                        </li>
                        <li>
                            Floodplain natural landcover is measured from the overall percent of natural landcover
                            throughout the entire functional network.
                        </li>
                    </ol>
                </section>
            </div>
        </div>
    )
}

export default NaturalLandcover
