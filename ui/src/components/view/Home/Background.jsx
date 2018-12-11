import React from "react"

import Section from "./Section"
import { scrollIntoView } from "../../../utils/dom"

import { ReactComponent as HighSinuosityIcon } from "../../../img/sinuosity_high.svg"
import { ReactComponent as LowSinuosityIcon } from "../../../img/sinuosity_low.svg"
import { ReactComponent as HighSizeClassesIcon } from "../../../img/size_classes_high.svg"
import { ReactComponent as LowSizeClassesIcon } from "../../../img/size_classes_low.svg"
import { ReactComponent as HighLengthIcon } from "../../../img/length_high.svg"
import { ReactComponent as LowLengthIcon } from "../../../img/length_low.svg"
import { ReactComponent as HighLandcoverIcon } from "../../../img/nat_landcover_high.svg"
import { ReactComponent as LowLandcoverIcon } from "../../../img/nat_landcover_low.svg"


function Background() {
    return (
        <React.Fragment>
            <Section title="How are aquatic barriers prioritized for removal?">
                <section>
                    <p>
                        In order to prioritize dams for removal, they are first characterized based on metrics that
                        describe the quality and status of their functional networks:
                    </p>
                    <ul>
                        <li>
                            <a onClick={() => scrollIntoView("NetworkLengthDef")}>Network length</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("NetworkSinuosityDef")}>Network sinuosity</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("NetworkComplexityDef")}>Network complexity</a>
                        </li>
                        <li>
                            <a onClick={() => scrollIntoView("NaturalLandcoverDef")}>Floodplain natural landcover</a>
                        </li>
                    </ul>

                    <p>
                        <br />
                        <br />
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
                    <br />
                    <br />
                    <p>TODO: explain the scoring approach</p>
                    <p>Using this tool, you can select the scenario that best meets your needs.</p>
                </section>
                <section>
                    <h3 id="NetworkLengthDef" className="is-size-3 flex-container flex-align-center">
                        <HighLengthIcon />
                        <div>Metric: network length</div>
                    </h3>
                    <p>
                        Network length measures the amount of connected aquatic network length that would be added to
                        the network by removing the barrier. It is the smaller of either the total upstream network
                        length or total downstream network length for the networks subdivided by this barrier. This is
                        because a barrier may have a very large upstream network, but if there is another barrier
                        immediately downstream, the overall effect of removing this barrier will be quite small.
                    </p>
                    <div className="prioritization-details flex-container flex-justify-space-between">
                        <div>
                            <HighLengthIcon />
                            <h4 className="is-size-4 text-align-center">High Network Length</h4>
                            <p>
                                Barriers that have large upstream and downstream networks will contribute a large amount
                                of connected aquatic network length if they are removed.
                            </p>
                        </div>
                        <div>
                            <LowLengthIcon />
                            <h4 className="is-size-4 text-align-center">Low Network Length</h4>
                            <p>
                                Barriers that have small upstream or downstream networks contribute relatively little
                                connected aquatic network length if removed.
                            </p>
                        </div>
                    </div>
                    <h5 className="title is-5">Methods:</h5>
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
                <section>
                    <h3 id="NetworkSinuosityDef" className="is-size-3 flex-container flex-align-center">
                        <HighSinuosityIcon />
                        <div>Metric: network sinuosity</div>
                    </h3>
                    <p>
                        Network sinuosity is a measure of how much the path of the river or stream deviates from a
                        straight line. In general, rivers and streams that are more sinuous generally indicate those
                        that have lower alteration from human disturbance such as channelization and diking, whereas
                        rivers that have been extensively altered tend to be less sinous.
                    </p>
                    <div className="prioritization-details flex-container flex-justify-space-between">
                        <div>
                            <HighSinuosityIcon />
                            <h4 className="is-size-4 text-align-center">High Sinuosity</h4>
                            <p>
                                Rivers and streams with high sinuosity are likely less altered by artificial
                                channelization and may have a wider variety of in-stream habitat. Barriers with more
                                sinuous upstream networks may contribute more natural habitat if removed.
                            </p>
                        </div>
                        <div>
                            <LowSinuosityIcon />
                            <h4 className="is-size-4 text-align-center">Low Sinuosity</h4>
                            <p>
                                Rivers and streams with lower sinuosity may be more altered by artificial channelization
                                and may have a lower variety of in-stream habitat. Barriers with less sinuous upstream
                                networks may contribute less natural habitat if removed.
                            </p>
                        </div>
                    </div>
                    <h5 className="title is-5">Methods:</h5>
                    <ol>
                        <li>
                            The sinuosity of each stream is calculated as the ratio between the length of that reach and
                            the straight line distance between the endpoints of that reach. The greater the total length
                            compared to the straight line distance, the higher the sinuosity.
                        </li>
                        <li>
                            Reaches are combined using a length-weighted average to calculate the overall sinuosity of
                            each functional network
                        </li>
                    </ol>
                </section>

                <section>
                    <h3 id="NetworkComplexityDef" className="is-size-3 flex-container flex-align-center">
                        <HighSizeClassesIcon />
                        <div>Metric: network complexity</div>
                    </h3>
                    <p>
                        A barrier that has upstream tributaries of different size classes, such as small streams, small
                        rivers, and large rivers, would contribute a more complex connected aquatic network if it was
                        removed. In contrast, a barrier with fewer upstream tributaries may contribute few if any size
                        classes to the network if removed. In general, a more complex network composed of a greater
                        range of size classes is more likely to have a wide range of available habitat for a greater
                        number of aquatic species.
                    </p>
                    <div className="prioritization-details flex-container flex-justify-space-between">
                        <div>
                            <HighSizeClassesIcon />
                            <h4 className="is-size-4 text-align-center">More size classes gained</h4>
                            <p>
                                Barriers that have several size classes upstream are more likely to contribute a more
                                complex network with a greater range of aquatic habitat for a greater variety of
                                species.
                            </p>
                        </div>
                        <div>
                            <LowSizeClassesIcon />
                            <h4 className="is-size-4 text-align-center">No size classes gained</h4>
                            <p>
                                Barriers that do not contribute any additional size classes are less likely to
                                contribute a wide range of aquatic habitat.
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
                </section>

                <section>
                    <h3 id="NaturalLandcoverDef" className="is-size-3 flex-container flex-align-center">
                        <HighLandcoverIcon />
                        <div>Metric: floodlplain natural landcover</div>
                    </h3>
                    <p>
                        Rivers and streams that have a greater amount of natural landcover in their floodplain are more
                        likely to have higher quality aquatic habitat. These areas may have more cool-water refugia for
                        temperature sensitive species due to shading from the overstory, and may have fewer water
                        quality issues. In contrast, rivers that have less natural landcover are more likely to be
                        altered and have impaired water quality.
                    </p>
                    <div className="prioritization-details flex-container flex-justify-space-between">
                        <div>
                            <HighLandcoverIcon />
                            <h4 className="is-size-4 text-align-center">High Natural Landcover</h4>
                            <p>
                                Barriers with aquatic networks that have more natural landcover are more likely to
                                contribute higher quality habitat if they are removed.
                            </p>
                        </div>
                        <div>
                            <LowLandcoverIcon />
                            <h4 className="is-size-4 text-align-center">Low Natural Landcover</h4>
                            <p>
                                Barriers with less natural landcover are less likely to contribute high quality habitat
                                for aquatic species if removed.
                            </p>
                        </div>
                    </div>
                    <h5 className="title is-5">Methods:</h5>
                    <ol>
                        <li>Floodplains are delineated using: TODO: floodplain methods from Kat</li>
                        <li>Natural landcover is derived from ... TODO: methods from Kat... </li>
                        <li>Natural landcover is clipped to the floodplain area for analysis</li>
                        <li>
                            The contributing watershed (catchment) of each stream and river reach is extracted from the
                            NHDPlus dataset
                        </li>
                        <li>
                            The total amount of area in natural landcover and total floodplain area are tallied for each
                            functional network
                        </li>
                        <li>
                            Floodplain natural landcover is measured from the overall percent of natural landcover
                            throughout the entire functional network
                        </li>
                    </ol>
                </section>

                <section>
                    <h3 id="NetworkConnectivityDef" className="is-size-3">
                        Scenario: network connectivity
                    </h3>
                    <p>
                        The network connectivity score prioritizes barriers on the amount of overall connected network
                        length they would contribute if removed. This is calculated by ranking barriers from those that
                        contribute the most network length to the least.
                        <br />
                        <br />
                        This scenario is most useful if you are ... TODO
                    </p>
                </section>

                <section>
                    <h3 id="WatershedConditionDef" className="is-size-3">
                        Scenario: watershed condition
                    </h3>
                    <p>
                        The watershed scenario is calculated by ranking barriers based on their combined scores of
                        network sinuosity, network complexity, and amount of natural landcover in the floodplains. Each
                        of these metrics is weighted equally.
                        <br />
                        <br />
                        This scenario is most useful if you are ... TODO
                    </p>
                </section>

                <section>
                    <h3 id="CombinedScoreDef" className="is-size-3">
                        Scenario: network connectivity and watershed condition
                    </h3>
                    <p>
                        This scenario combines the network connectivity and watershed condition scores into a single
                        score. Network connectivity and watershed condition are weighted equally relative to each other.
                        <br />
                        <br />
                        This scenario is most useful if you are ... TODO
                    </p>
                </section>
            </Section>
        </React.Fragment>
    )
}

export default Background
