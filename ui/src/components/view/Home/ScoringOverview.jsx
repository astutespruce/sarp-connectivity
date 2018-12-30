import React from "react"
import { Link } from "react-router-dom"

import networkLength from "../../../img/length_high.svg"
import networkComplexity from "../../../img/size_classes_high.svg"
import networkSinuosity from "../../../img/sinuosity_high.svg"
import naturalLandcover from "../../../img/nat_landcover_high.svg"
import functionalNetwork from "../../../img/functional_network.svg"

// Photo from: https://www.flickr.com/photos/savannahcorps/9272554306/
import damImage from "../../../img/9272554306_b34bf886f4_z.jpg"

const ScoringOverview = () => (
    <React.Fragment>
        <section>
            <h3 className="title is-3">How are barriers prioritized for removal?</h3>
            <h4 className="subtitle is-4 flex-container flex-align-center" style={{ marginTop: "1rem" }}>
                <div className="circle-dark">
                    <div>1</div>
                </div>
                <div>Aquatic barriers are identified and measured for their potential impact on aquatic organisms:</div>
            </h4>
            <div className="columns">
                <div className="column is-two-thirds">
                    <p>
                        Aquatic barriers are natural and human-made structures that impede the passage of aquatic
                        organisms through the river network.
                        <br />
                        <br />
                        They include:
                    </p>
                    <ul className="list-disc">
                        <li>Waterfalls</li>
                        <li>Dams</li>
                        <li>Road-related barriers</li>
                    </ul>
                    <p>
                        <br />
                        Where possible, human-made barriers have been assessed using field reconnaissance to determine
                        their likely impact on aquatic organisms as well as their feasibility of removal. You can
                        leverage these characteristics to select a smaller number of barriers to prioritize.
                    </p>
                </div>
                <div className="column">
                    <img src={damImage} alt="Hartwell Dam" />
                    <div className="is-size-7 has-text-grey">
                        <a
                            href="https://www.flickr.com/photos/savannahcorps/9272554306/"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Hartwell Dam, Georgia. Billy Birdwell, U.S. Army Corps of Engineers.
                        </a>
                    </div>
                </div>
            </div>
        </section>

        <section>
            <h4 className="subtitle is-4 flex-container flex-align-center" style={{ marginTop: "1rem" }}>
                <div className="circle-dark">
                    <div>2</div>
                </div>
                <div>Aquatic barriers are measured for their impact on the aquatic network:</div>
            </h4>
            <div className="columns">
                <div className="column is-two-thirds">
                    <p>
                        Functional aquatic networks are the stream and river reaches that extend upstream from a barrier
                        or river mouth to either the origin of that stream or the next upstream barrier. They form the
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
                        NHDPlus Medium Resolution version was the only one available. Where possible, their locations
                        were manually inspected to verify their correct position on the aquatic network.
                        <br />
                        <br />
                        <span className="icon">
                            <i className="fas fa-exclamation-triangle" />
                        </span>
                        <span className="has-text-grey">
                            Note: due to limitations of existing data sources for aquatic networks, not all aquatic
                            barriers can be correctly located on the aquatic networks. These barriers are not included
                            in the network connectivity analysis and cannot be prioritized using this tool. However,
                            these data can still be downloaded from this tool and used for offline analysis.
                        </span>
                    </p>
                </div>
                <div className="column">
                    <img src={functionalNetwork} alt="Functional Network Graphic" style={{ height: "30rem" }} />
                </div>
            </div>
        </section>

        <section>
            <h4 className="subtitle is-4 flex-container flex-align-center">
                <div className="circle-dark">
                    <div>3</div>
                </div>
                <div>
                    Barriers are characterized using metrics that describe the quality and status of their functional
                    networks:
                </div>
            </h4>

            <div className="columns">
                <div className="column">
                    <div className="info-box">
                        <h3 className="subtitle is-3 flex-container flex-align-center">
                            <img src={networkLength} alt="Network length graphic" />
                            Network Length
                        </h3>
                        <p>
                            Network length measures the amount of connected aquatic network length that would be added
                            to the network by removing the barrier. Longer connected networks may provide more overall
                            aquatic habitat for a wider variety of organisms and better support dispersal and migration.
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
                            Network complexity measures the number of unique upstream size classes that would be added
                            to the network by removing the barrier. A barrier that has upstream tributaries of different
                            size classes, such as small streams, small rivers, and large rivers, would contribute a more
                            complex connected aquatic network if it was removed.
                            <br />
                            <Link to="/metrics/complexity">Read more...</Link>
                        </p>
                    </div>
                </div>
            </div>

            <div className="columns">
                <div className="column">
                    <div className="info-box">
                        <h3 className="subtitle is-3 flex-container flex-align-center">
                            <img src={networkSinuosity} alt="Network sinuosity graphic" />
                            Network Sinuosity
                        </h3>
                        <p>
                            Network sinuosity measures the amount that the path of the river or stream deviates from a
                            straight line. In general, rivers and streams that are more sinuous generally indicate those
                            that have lower alteration from human disturbance such as channelization and diking.
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
                            Natural landcover measures the amount of area within the floodplain of the upstream aquatic
                            network that is in natural landcover. Rivers and streams that have a greater amount of
                            natural landcover in their floodplain are more likely to have higher quality aquatic
                            habitat.
                            <br />
                            <Link to="/metrics/landcover">Read more...</Link>
                        </p>
                    </div>
                </div>
            </div>
        </section>
        <section>
            <h4 className="subtitle is-4 flex-container flex-align-center">
                <div className="circle-dark">
                    <div>4</div>
                </div>
                <div>
                    Metrics are combined and ranked to create three scenarios for prioritizing barriers for removal:
                </div>
            </h4>

            <div className="columns">
                <div className="column">
                    <div className="info-box">
                        <h3 className="subtitle is-3 text-align-center">Network Connectivity</h3>
                        <p>
                            Aquatic barriers prioritized according to network connectivity are driven exclusively on the
                            total amount of functional aquatic network that would be reconnected if a given dam was
                            removed. This is driven by the&nbsp;
                            <Link to="/metrics/length">network length</Link> metric. No consideration is given to other
                            characteristics that measure the quality and condition of those networks.
                        </p>
                    </div>
                </div>

                <div className="column">
                    <div className="info-box">
                        <h3 className="subtitle is-3 text-align-center">Watershed Condition</h3>
                        <p>
                            Aquatic barriers prioritized according to watershed condition are driven by metrics related
                            to the overall quality of the aquatic network that would be reconnected if a given dam was
                            removed. It is based on a combination of&nbsp;
                            <Link to="/metrics/complexity">network complexity</Link>
                            ,&nbsp;
                            <Link to="/metrics/sinuosity">network sinuosity</Link>, and&nbsp;
                            <Link to="/metrics/landcover">floodplain natural landcover</Link>. Each of these metrics is
                            weighted equally.
                        </p>
                    </div>
                </div>
            </div>

            <div className="columns info-boxes">
                <div className="column">
                    <div className="info-box">
                        <h3 className="subtitle is-3 text-align-center">Network Connectivity + Watershed Condition</h3>
                        <p>
                            Aquatic barriers prioritized according to combined network connectivity and watershed
                            condition are driven by both the length and quality of the aquatic networks that would be
                            reconnected if these barriers are removed. <b>Network connectivity</b> and{" "}
                            <b>watershed condition</b> are weighted equally.
                        </p>
                    </div>
                </div>
            </div>

            <p style={{ marginTop: "2rem" }}>
                To reduce the impact of outliers, such as very long functional networks, barriers are scored based on
                their relative rank within the overall range of unique values for a given metric. Many barriers have the
                same value for a given metric and are given the same relative score; this causes the distribution of
                values among scores to be highly uneven in certain areas.
                <br />
                <br />
                Once barriers have been scored for each of the above scenarios, they are binned into 20 tiers to
                simplify interpretation and use. To do this, barriers that fall in the best 5% of the range of scores
                for that metric are assigned to Tier 1 (top tier), whereas barriers that fall in the worst 5% of the
                range of scores for that metric are assigned Tier 20 (bottom tier).
                <br />
                <br />
                <i className="fas fa-exclamation-triangle" />
                &nbsp; Note: tiers are based on position within the range of observed scores for a given area. They are{" "}
                <i>not</i> based on the frequency of scores, such as percentiles, and therefore may have a highly uneven
                number of dams per tier depending on the area. In general, there are fewer barriers in the top tiers
                than there are in the bottom tiers. This is largely because many barriers share the same value for a
                given metric.
            </p>
        </section>
    </React.Fragment>
)

export default ScoringOverview
