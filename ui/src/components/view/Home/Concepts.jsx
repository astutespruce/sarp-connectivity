import React from "react"
import { Link } from "react-router-dom"

import functionalNetwork from "../../../img/functional_network.svg"

import networkLength from "../../../img/length_high.svg"
import networkComplexity from "../../../img/size_classes_high.svg"
import networkSinuosity from "../../../img/sinuosity_high.svg"
import naturalLandcover from "../../../img/nat_landcover_high.svg"

// Photo from: https://www.flickr.com/photos/savannahcorps/9272554306/
import DamImage2 from "../../../img/9272554306_b34bf886f4_z.jpg"

// Photo from: https://www.flickr.com/photos/usfwssoutheast/33643110826/in/album-72157675681441135/
import CaneRiverDam from "../../../img/33643110826_a90387d592_z.jpg"

function Concepts() {
    return (
        <div className="container">
            <section>
                <h3 className="title is-3">Aquatic Barriers</h3>
                <div className="columns">
                    <div className="column is-two-thirds">
                        <p>
                            These barriers are natural and human-made structures that impede the passage of aquatic
                            organisms through the river network. Some human-made barriers may no longer serve their
                            original purpose and have fallen into disrepair. These barriers may be particularly good
                            candidates for removal or remediation to restore aquatic connectivity.
                            <br />
                            <br />
                            Aquatic barriers include:
                        </p>
                        <ul>
                            <li>Waterfalls (from the USGS Waterfalls Inventory)</li>
                            <li>Dams</li>
                            <li>Road-related barriers (culverts, fords, and similar potential aquatic barriers)</li>
                        </ul>
                        <p>
                            <br />
                            Not all barriers completely block the passage of all aquatic organisms. In this tool
                            waterfalls and dams are considered &quot;hard&quot; barriers that divide the aquatic
                            network. Road-related barriers require field reconnaissance to determine if they are true
                            barriers in the aquatic network.
                        </p>
                    </div>
                    <div className="column">
                        <img src={CaneRiverDam} alt="Cane River Dam Ruins" />
                        <img src={DamImage2} alt="Hartwell Dam" style={{ marginTop: "3rem" }} />
                    </div>
                </div>
            </section>
            <section>
                <h3 className="title is-3">Functional Networks</h3>
                <div className="columns">
                    <div className="column is-two-thirds">
                        <p>
                            Functional networks are the stream and river reaches that extend upstream from a barrier or
                            river mouth to either the origin of that stream or the next upstream barrier. They form the
                            basis for the aquatic network metrics used in this tool.
                            <br />
                            <br />
                            To calculate functional networks, all barriers were snapped to the&nbsp;
                            <a
                                href="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                USGS High Resolution National Hydrography Dataset
                            </a>
                            &nbsp;(NHDPlus) for all areas except the lower Mississipi (hydrologic region 8), where the
                            NHDPlus Medium Resolution version was the only one available. Where possible, their
                            locations were manually inspected to verify their correct position on the aquatic network.
                            <br />
                            <br />
                            <span className="icon">
                                <i className="fas fa-exclamation-triangle" />
                            </span>
                            <span className="has-text-grey">
                                Note: due to limitations of existing data sources for aquatic networks, not all aquatic
                                barriers can be correctly located on the aquatic networks. These barriers are not
                                included in the network connectivity analysis and cannot be prioritized using this tool.
                                However, these data can still be downloaded from this tool and used for offline
                                analysis.
                            </span>
                        </p>
                    </div>
                    <div className="column">
                        <img src={functionalNetwork} alt="Functional Network Graphic" style={{ height: "30rem" }} />
                    </div>
                </div>
            </section>

            <section>
                <h3 className="title is-3">How are barriers prioritized for removal?</h3>
                <h4 className="subtitle is-4">
                    In order to prioritize dams for removal, they are first characterized using metrics that describe
                    the quality and status of their functional networks:
                </h4>

                <div className="columns info-boxes">
                    <div className="column">
                        <div className="info-box">
                            <div>
                                <h3 className="subtitle is-3 flex-container flex-align-center">
                                    <img src={networkLength} alt="Network length graphic" />
                                    Network Length
                                </h3>
                            </div>
                            <p>
                                Network length measures the amount of connected aquatic network length that would be
                                added to the network by removing the barrier. Longer connected networks may provide more
                                overall aquatic habitat for a wider variety of organisms and better support dispersal
                                and migration.
                                <br />
                                <br />
                                <Link to="/metrics/length">Read more...</Link>
                            </p>
                        </div>
                    </div>

                    <div className="column">
                        <div className="info-box">
                            <h3 className="subtitle is-3 flex-container flex-align-center">
                                <img src={networkComplexity} alt="Network complexity graphic" />
                                Network Complexity
                            </h3>
                            <p>
                                Network complexity measures the number of unique upstream size classes that would be
                                added to the network by removing the barrier. A barrier that has upstream tributaries of
                                different size classes, such as small streams, small rivers, and large rivers, would
                                contribute a more complex connected aquatic network if it was removed.
                                <br />
                                <Link to="/metrics/complexity">Read more...</Link>
                            </p>
                        </div>
                    </div>
                </div>

                <div className="columns info-boxes">
                    <div className="column">
                        <div className="info-box">
                            <h3 className="subtitle is-3 flex-container flex-align-center">
                                <img src={networkSinuosity} alt="Network sinuosity graphic" />
                                Network Sinuosity
                            </h3>
                            <p>
                                Network sinuosity measures the amount that the path of the river or stream deviates from
                                a straight line. In general, rivers and streams that are more sinuous generally indicate
                                those that have lower alteration from human disturbance such as channelization and
                                diking.
                                <br />
                                <Link to="/metrics/sinuosity">Read more...</Link>
                            </p>
                        </div>
                    </div>

                    <div className="column">
                        <div className="info-box">
                            <h3 className="subtitle is-3 flex-container flex-align-center">
                                <img src={naturalLandcover} alt="Network complexity graphic" />
                                Natural landcover
                            </h3>
                            <p>
                                Natural landcover measures the amount of area within the floodplain of the upstream
                                aquatic network that is in natural landcover. Rivers and streams that have a greater
                                amount of natural landcover in their floodplain are more likely to have higher quality
                                aquatic habitat.
                                <br />
                                <Link to="/metrics/landcover">Read more...</Link>
                            </p>
                        </div>
                    </div>
                </div>
            </section>
            <section>
                <h4 className="subtitle is-4">
                    These metrics are then combined to create three scenarios for prioritizing barriers for removal:
                </h4>

                <div className="columns info-boxes">
                    <div className="column">
                        <div className="info-box">
                            <h3 className="subtitle is-3 text-align-center">Network Connectivity</h3>
                            <p>
                                Aquatic barriers prioritized according to network connectivity are driven exclusively on
                                the total amount of functional aquatic network that would be reconnected if a given dam
                                was removed. This is driven by the&nbsp;
                                <Link to="/metrics/length">network length</Link> metric. No consideration is given to
                                other characteristics that measure the quality and condition of those networks.
                            </p>
                        </div>
                    </div>

                    <div className="column">
                        <div className="info-box">
                            <h3 className="subtitle is-3 text-align-center">Watershed Condition</h3>
                            <p>
                                Aquatic barriers prioritized according to watershed condition are driven by metrics
                                related to the overall quality of the aquatic network that would be reconnected if a
                                given dam was removed. It is based on a combination of&nbsp;
                                <Link to="/metrics/complexity">network complexity</Link>
                                ,&nbsp;
                                <Link to="/metrics/sinuosity">network sinuosity</Link>, and&nbsp;
                                <Link to="/metrics/landcover">floodplain natural landcover</Link>. Each of these metrics
                                is weighted equally.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="columns info-boxes">
                    <div className="column">
                        <div className="info-box">
                            <h3 className="subtitle is-3 text-align-center">
                                Network Connectivity + Watershed Condition
                            </h3>
                            <p>
                                Aquatic barriers prioritized according to combined network connectivity and watershed
                                condition are driven by both the length and quality of the aquatic networks that would
                                be reconnected if these barriers are removed. <b>Network connectivity</b> and{" "}
                                <b>watershed condition</b> are weighted equally.
                            </p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}

export default Concepts
