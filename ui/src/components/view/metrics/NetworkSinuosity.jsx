import React, { useEffect } from "react"

import { scrollIntoView } from "../../../utils/dom"

import highSinuosityIcon from "../../../img/sinuosity_high.svg"
import lowSinuosityIcon from "../../../img/sinuosity_low.svg"

import headerImage from "../../../img/carl-cerstrand-79627-unsplash.jpg"

function NetworkSinuosity() {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })
    return (
        <div id="ContentPage">
            <div className="image-header" style={{ backgroundImage: `url(${headerImage})` }}>
                <div className="credits">
                    Photo credit:{" "}
                    <a href="https://unsplash.com/photos/J2bNC9gW5NI" target="_blank" rel="noopener noreferrer">
                        Carl Cerstrand
                    </a>
                </div>
            </div>
            <div className="container">
                <section className="page-header">
                    <h1 className="title is-1 is-large">Network sinuosity</h1>
                    <p className="is-size-4">
                        Network sinuosity is a measure of how much the path of the river or stream deviates from a
                        straight line. In general, rivers and streams that are more sinuous generally indicate those
                        that have lower alteration from human disturbance such as channelization and diking, whereas
                        rivers that have been extensively altered tend to be less sinuous. Sinuosity ranges from low
                        (&lt;1.2) to moderate (1.2 - 1.5) to high (&gt;1.5) (Rosgen, 1996).
                    </p>
                </section>

                <section>
                    <div className="columns">
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={lowSinuosityIcon} alt="Network sinuosity graphic" />
                                    Low sinuosity
                                </h3>
                                <p>
                                    Rivers and streams with lower sinuosity may be more altered by artificial
                                    channelization and may have a lower variety of in-stream habitat. Barriers with less
                                    sinuous upstream networks may contribute less natural habitat if removed.
                                </p>
                            </div>
                        </div>
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={highSinuosityIcon} alt="Network sinuosity graphic" />
                                    High sinuosity
                                </h3>
                                <p>
                                    Rivers and streams with high sinuosity are likely less altered by artificial
                                    channelization and may have a wider variety of in-stream habitat. Barriers with more
                                    sinuous upstream networks may contribute more natural habitat if removed.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <h3 className="subtitle is-3">Methods:</h3>
                    <ol>
                        <li>
                            The sinuosity of each stream is calculated as the ratio between the length of that reach and
                            the straight line distance between the endpoints of that reach. The greater the total length
                            compared to the straight line distance, the higher the sinuosity.
                        </li>
                        <li>
                            Reaches are combined using a length-weighted average to calculate the overall sinuosity of
                            each functional network.
                        </li>
                    </ol>
                </section>
                <section>
                    <h3 className="subtitle is-3">References:</h3>
                    <ul>
                        <li>
                            Rosgen, David L. 1996. Applied river morphology. Pagosa Springs, Colo: Wildland Hydrology.
                        </li>
                    </ul>
                </section>
            </div>
        </div>
    )
}

export default NetworkSinuosity
