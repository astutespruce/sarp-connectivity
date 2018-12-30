import React, { useEffect } from "react"

import { scrollIntoView } from "../../../utils/dom"

import highSizeClassesIcon from "../../../img/size_classes_high.svg"
import lowSizeClassesIcon from "../../../img/size_classes_low.svg"

import headerImage from "../../../img/david-kovalenko-447548-unsplash.jpg"

function NetworkComplexity() {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })
    return (
        <div id="ContentPage">
            <div className="image-header" style={{ backgroundImage: `url(${headerImage})` }}>
                <div className="credits">
                    Photo credit:{" "}
                    <a href="https://unsplash.com/photos/qYMa2-P-U0M" target="_blank" rel="noopener noreferrer">
                        David Kovalenko
                    </a>
                </div>
            </div>

            <div className="container" style={{ paddingBottom: "6rem" }}>
                <section className="page-header">
                    <h1 className="title is-1 is-large">Network complexity</h1>
                    <p className="is-size-4">
                        A barrier that has upstream tributaries of different size classes, such as small streams, small
                        rivers, and large rivers, would contribute a more complex connected aquatic network if it was
                        removed. In contrast, a barrier with fewer upstream tributaries may contribute few if any size
                        classes to the network if removed. In general, a more complex network composed of a greater
                        range of size classes is more likely to have a wide range of available habitat for a greater
                        number of aquatic species.
                    </p>
                </section>
                
                <section>
                    <div className="columns">
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={lowSizeClassesIcon} alt="low size classes graphic" />
                                    No size classes gained
                                </h3>
                                <p>
                                    Barriers that do not contribute any additional size classes are less likely to
                                    contribute a wide range of aquatic habitat.
                                </p>
                            </div>
                        </div>
                        <div className="column">
                            <div className="info-box">
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={highSizeClassesIcon} alt="high size classes graphic" />
                                    Several size classes gained
                                </h3>
                                <p>
                                    Barriers that have several size classes upstream are more likely to contribute a
                                    more complex network with a greater range of aquatic habitat for a greater variety
                                    of species.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <h3 className="subtitle is-3">Methods:</h3>
                    <ol>
                        <li>
                            Stream and river reaches were assigned to size classes based on total drainage area:
                            <ul>
                                <li>
                                    Headwaters: &lt; 10 km
                                    <sup>2</sup>
                                </li>
                                <li>
                                    Creeks: &ge; 10 km
                                    <sup>2</sup> and &lt; 100 km
                                    <sup>2</sup>
                                </li>
                                <li>
                                    Small rivers: &ge; 100 km
                                    <sup>2</sup> and &lt; 518 km
                                    <sup>2</sup>
                                </li>
                                <li>
                                    Medium tributary rivers: &ge; 519 km
                                    <sup>2</sup> and &lt; 2,590 km
                                    <sup>2</sup>
                                </li>
                                <li>
                                    Medium mainstem rivers: &ge; 2,590 km
                                    <sup>2</sup> and &lt; 10,000 km
                                    <sup>2</sup>
                                </li>
                                <li>
                                    Large rivers: &ge; 10,000 km
                                    <sup>2</sup> and &lt; 25,000 km
                                    <sup>2</sup>
                                </li>
                                <li>
                                    Great rivers: &ge; 25,000 km
                                    <sup>2</sup>
                                </li>
                            </ul>
                        </li>
                        <li>
                            Each barrier is assigned the total number of unique size classes in its upstream functional
                            network.
                        </li>
                    </ol>
                </section>
            </div>
        </div>
    )
}

export default NetworkComplexity
