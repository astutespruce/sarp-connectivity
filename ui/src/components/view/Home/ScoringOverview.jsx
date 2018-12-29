import React from "react"
import { Link } from "react-router-dom"

import Section from "../../Section"

// From https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/
// import ForestStream from "../../../img/6882770647_60c0d68a9c_z.jpg"

// From: https://www.flickr.com/photos/usfwssoutheast/7983183705/in/album-72157631529358797/
// import DamRemoval from "../../../img/7983183705_4187ce9631_z.jpg"

import networkLength from "../../../img/length_high.svg"
import networkComplexity from "../../../img/size_classes_high.svg"
import networkSinuosity from "../../../img/sinuosity_high.svg"
import naturalLandcover from "../../../img/nat_landcover_high.svg"

function ScoringOverview() {
    return (
        <Section title="How are barriers prioritized for removal?">
            <p>
                In order to prioritize dams for removal, they are first characterized using metrics that describe the
                quality and status of their functional networks:
                <br />
                <br />
            </p>

            <div className="columns info-boxes">
                <div className="column">
                    <div className="info-box-content">
                        <div className="flex-container flex-align-center info-box-header">
                            <img src={networkLength} alt="Network length graphic" />
                            <h3 className="subtitle is-3">Network Length</h3>
                        </div>
                        <p>
                            Network length measures the amount of connected aquatic network length that would be added
                            to the network by removing the barrier. Longer connected networks may provide more overall
                            aquatic habitat for a wider variety of organisms and better support dispersal and migration.
                            <br />
                            <Link to="/metrics/length">Read more...</Link>
                        </p>
                    </div>
                </div>

                <div className="column">
                    <div className="info-box-content">
                        <div className="flex-container flex-align-center info-box-header">
                            <img src={networkComplexity} alt="Network complexity graphic" />
                            <h3 className="subtitle is-3">Network Complexity</h3>
                        </div>
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

            <div className="columns info-boxes">
                <div className="column">
                    <div className="info-box-content">
                        <div className="flex-container flex-align-center info-box-header">
                            <img src={networkSinuosity} alt="Network length graphic" />
                            <h3 className="subtitle is-3">Network Sinuosity</h3>
                        </div>
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
                    <div className="info-box-content">
                        <div className="flex-container flex-align-center info-box-header">
                            <img src={naturalLandcover} alt="Network complexity graphic" />
                            <h3 className="subtitle is-3">Natural landcover</h3>
                        </div>
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

            <p>
                <br />
                These metrics are then combined to create three scenarios for prioritizing barriers for removal:
                <br />
                <br />
            </p>

            <div className="columns info-boxes">
                <div className="column">
                    <div className="info-box-content">
                        <div className="info-box-header">
                            <h3 className="subtitle is-3 text-align-center">Network Connectivity</h3>
                        </div>
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
                    <div className="info-box-content">
                        <div className="info-box-header">
                            <h3 className="subtitle is-3 text-align-center">Watershed Condition</h3>
                        </div>
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
                    <div className="info-box-content">
                        <div className="info-box-header">
                            <h3 className="subtitle is-3 text-align-center">
                                Network Connectivity &amp; Watershed Condition
                            </h3>
                        </div>
                        <p>
                            Aquatic barriers prioritized according to combined network connectivity and watershed
                            condition are driven by both the length and quality of the aquatic networks that would be
                            reconnected if these barriers are removed. <b>Network connectivity</b> and{" "}
                            <b>watershed condition</b> are weighted equally.
                        </p>
                    </div>
                </div>
            </div>
        </Section>
    )
}

export default ScoringOverview
