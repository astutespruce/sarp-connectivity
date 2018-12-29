import React, { useEffect } from "react"

import { scrollIntoView } from "../../../utils/dom"
import Section from "../../Section"

import highSizeClassesIcon from "../../../img/size_classes_high.svg"
import lowSizeClassesIcon from "../../../img/size_classes_low.svg"

function NetworkComplexity() {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })
    return (
        <div id="ContentPage" className="view">
            <Section id="NetworkComplexityDef" title="Network Complexity">
                <p>
                    A barrier that has upstream tributaries of different size classes, such as small streams, small
                    rivers, and large rivers, would contribute a more complex connected aquatic network if it was
                    removed. In contrast, a barrier with fewer upstream tributaries may contribute few if any size
                    classes to the network if removed. In general, a more complex network composed of a greater range of
                    size classes is more likely to have a wide range of available habitat for a greater number of
                    aquatic species.
                </p>
                <div className="prioritization-details flex-container flex-justify-space-between">
                    <div>
                        <img src={highSizeClassesIcon} alt="High Size Classes" />
                        <h4 className="is-size-4 text-align-center">More size classes gained</h4>
                        <p>
                            Barriers that have several size classes upstream are more likely to contribute a more
                            complex network with a greater range of aquatic habitat for a greater variety of species.
                        </p>
                    </div>
                    <div>
                        <img src={lowSizeClassesIcon} alt="Low Size Classes" />
                        <h4 className="is-size-4 text-align-center">No size classes gained</h4>
                        <p>
                            Barriers that do not contribute any additional size classes are less likely to contribute a
                            wide range of aquatic habitat.
                        </p>
                    </div>
                </div>
                <h5 className="title is-5">Methods:</h5>
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
            </Section>
        </div>
    )
}

export default NetworkComplexity
