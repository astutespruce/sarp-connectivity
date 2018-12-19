import React from "react"

import WaterStonesImage from "../../../img/robert-zunikoff-409755-unsplash.jpg"
import Section from "../Home/Section"

const Start = () => (
    <div id="ContentPage">
        <Section title="Prioritize Barriers for Removal" dark image={WaterStonesImage}>
            <div className="columns">
                <div className="column is-two-thirds">
                    <p className="text-help" style={{ marginBottom: "1rem" }}>
                        To prioritize barriers, you will work through the following steps:
                    </p>
                    <section className="step">
                        <h4 className="subtitle is-5">
                            <span className="step-number">1</span>
                            Select area of interest
                        </h4>
                        <p className="text-help">
                            You can select areas using state, county, watershed, and ecoregion boundaries.
                        </p>
                    </section>
                    <section className="step">
                        <h4 className="subtitle is-5">
                            <span className="step-number">2</span>
                            Filter barriers
                        </h4>
                        <p className="text-help">
                            You can filter barriers by feasibility, height, and other key characteristics to select
                            those that best meet your needs.
                        </p>
                    </section>
                    <section className="step">
                        <h4 className="is-size-4">
                            <span className="step-number">3</span>
                            Explore priorities on the map
                        </h4>
                        <p className="text-help">
                            Once you have defined your area of interest and selected the barriers you want, you can
                            explore them on the map.
                        </p>
                    </section>
                    <section className="step">
                        <h4 className="subtitle is-5">
                            <span className="step-number">4</span>
                            Download prioritized barriers
                        </h4>
                        <p className="text-help">
                            You can download the inventory for your area of interest and perform offline work.
                        </p>
                    </section>
                </div>
                <div className="column">
                    <div className="info-box">
                        <h4 className="is-size-4">What do you want to prioritize?</h4>
                        <div>
                            <button className="button is-info is-medium" type="button">
                                Dams
                            </button>
                            <button className="button is-info is-medium" type="button">
                                Road-related barriers
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </Section>
    </div>
)

export default Start
