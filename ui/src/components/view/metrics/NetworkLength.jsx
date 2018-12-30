import React, { useEffect } from "react"

import { scrollIntoView } from "../../../utils/dom"

import highLengthIcon from "../../../img/length_high.svg"
import lowLengthIcon from "../../../img/length_low.svg"

import headerImage from "../../../img/5149475130_6be3c887a8_o.jpg"

function NetworkLength() {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })
    return (
        <div id="ContentPage">
            <div className="image-header" style={{ backgroundImage: `url(${headerImage})` }}>
                <div className="credits">
                    Photo credit:{" "}
                    <a
                        href="https://www.flickr.com/photos/usfwssoutheast/5149475130/in/gallery-141606341@N03-72157697846677391/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Little Tennessee River, North Carolina. U.S. Fish and Wildlife Service.
                    </a>
                </div>
            </div>

            <div className="container" style={{ paddingBottom: "6rem" }}>
                <section className="page-header">
                    <h1 className="title is-1 is-large">Network length</h1>
                    <p className="is-size-4">
                        Network length measures the amount of connected aquatic network length that would be added to
                        the network by removing the barrier. It is the smaller of either the total upstream network
                        length or total downstream network length for the networks subdivided by this barrier. This is
                        because a barrier may have a very large upstream network, but if there is another barrier
                        immediately downstream, the overall effect of removing this barrier will be quite small.
                    </p>
                </section>

                <section>
                    <div className="columns">
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={lowLengthIcon} alt="Network length graphic" />
                                    Low network length
                                </h3>
                                <p>
                                    Barriers that have small upstream or downstream networks contribute relatively
                                    little connected aquatic network length if removed.
                                </p>
                            </div>
                        </div>
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={highLengthIcon} alt="Network length graphic" />
                                    High network length
                                </h3>
                                <p>
                                    Barriers that have large upstream and downstream networks will contribute a large
                                    amount of connected aquatic network length if they are removed.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>
                <section>
                    <h3 className="subtitle is-3">Methods:</h3>
                    <ol>
                        <li>
                            The total upstream length is calculated as the sum of the lengths of all upstream river and
                            stream reaches.
                        </li>
                        <li>
                            The total downstream length is calculated for the network immediately downstream of the
                            barrier. Note: this is the total network length of the downstream network, <i>not</i> the
                            shortest downstream path to the next barrier or river mouth.
                        </li>
                        <li>Network length is the smaller of the upstream or downstream network lengths.</li>
                    </ol>
                </section>
            </div>
        </div>
    )
}

export default NetworkLength
