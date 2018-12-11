import React from "react"
import { Link } from "react-router-dom"

import Section from "./Section"

import FishImage from "../../../img/iStock-181890680.jpg"

function Intro() {
    return (
        <Section
            id="HomeHeader"
            image={FishImage}
            dark
            title="Fish and other aquatic organisms"
            subtitle="depend on high quality, connected river networks."
        >
            <p>
                A legacy of human use of river networks have left them fragmented by barriers such as dams and culverts.
                Fragmentation prevents species from dispersing and accessing habitats required for their persistence
                through changing conditions.
                <br />
                <br />
                Recently improved inventories of aquatic barriers enable us to describe, understand, and prioritize them
                for removal, restoration, and mitigation. Through this tool and others, we empower you by providing
                information on documented barriers and standardized methods by which to prioritize barriers of interest
                for restoration efforts.
            </p>
            <div className="columns section">
                <div className="column">
                    <div className="box">
                        <div className="media">
                            <figure className="media-left">
                                <div className="icon is-medium">
                                    <span className="fa fa-chart-bar fa-2x" />
                                </div>
                            </figure>
                            <div className="media-content">
                                <div className="content">
                                    <h4 className="is-size-4">Summarize</h4>
                                </div>
                            </div>
                        </div>
                        <p>Explore summaries of small and large aquatic barriers across the southeast.</p>
                        <div className="has-text-centered is-size-5">
                            <Link to="/summary" style={{ color: "#3273dc" }}>
                                View regional summaries
                            </Link>
                        </div>
                    </div>
                </div>

                <div className="column">
                    <div className="box">
                        <div className="media">
                            <figure className="media-left">
                                <div className="icon is-medium">
                                    <span className="fa fa-search-location fa-2x" />
                                </div>
                            </figure>
                            <div className="media-content">
                                <div className="content">
                                    <h4 className="is-size-4">Prioritize</h4>
                                </div>
                            </div>
                        </div>
                        <p>Prioritize aquatic barriers for removal in your area of interest.</p>
                        <div className="has-text-centered is-size-5">
                            <Link to="/priority" style={{ color: "#3273dc" }}>
                                {" "}
                                Start prioritizing
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            <section className="has-text-centered has-text-grey-lighter">
                <h4 className="subtitle is-4 has-text-grey-lighter">Learn more about aquatic barriers...</h4>
                <div className="icon is-large">
                    <span className="fa fa-chevron-down fa-3x" />
                </div>
            </section>
        </Section>
    )
}

export default Intro
