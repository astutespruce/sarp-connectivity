import React from "react"
import { Link } from "react-router-dom"

import { formatNumber } from "../../../utils/format"

import summaryStats from "../../../data/summary_stats.json"
import summarizeImage from "../../../img/summarize.jpg"
import prioritizeImage from "../../../img/prioritize.jpg"
import SARPLogo from "../../../img/sarp_logo.png"

const { dams, barriers, miles } = summaryStats.southeast

function Intro() {
    return (
        <React.Fragment>
            <section className="page-header">
                <p className="is-size-4">
                    Aquatic connectivity is essential. Fish and other aquatic organisms depend on high quality,
                    connected river networks. A legacy of human use of river networks have left them fragmented by
                    barriers such as dams and culverts. Fragmentation prevents species from dispersing and accessing
                    habitats required for their persistence through changing conditions.
                    <br />
                    <br />
                    Recently improved inventories of aquatic barriers enable us to describe, understand, and prioritize
                    them for removal, restoration, and mitigation. Through this tool and others, we empower you by
                    providing information on documented barriers and standardized methods by which to prioritize
                    barriers of interest for restoration efforts.
                </p>
            </section>

            <section>
                <h3 className="title is-3">The Southeast Aquatic Barrier Inventory:</h3>
                <div className="columns">
                    <div className="column is-two-thirds">
                        <p>
                            This inventory is a growing and living database of dams, culverts, and other road crossings
                            compiled by the{" "}
                            <a href="https://southeastaquatics.net/" target="_blank" rel="noopener noreferrer">
                                Southeast Aquatic Resources Partnership
                            </a>{" "}
                            with the generous support from many partners and funders. The Inventory is the foundation of{" "}
                            <a
                                href="https://southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                SARP&apos;s Connectivity Program
                            </a>{" "}
                            because it empowers <Link to="/teams">Aquatic Connectivity Teams</Link> and other
                            collaborators with the best available information on aquatic barriers. The inventory
                            directly supports prioritization of barriers by including metrics that describe network
                            connectivity, landscape condition, and presence of threatened and endangered aquatic
                            organisms.
                            <br />
                            <br />
                            This inventory consists of datasets from local, state, and federal partners. It is
                            supplemented with input from partners with on the ground knowledge of specific structures.
                            The information on barriers is not complete or comprehensive across the region, and depends
                            on the availability and completeness of existing data and level of partner feedback. Some
                            areas of the region are more complete than others but none should be considered 100%
                            complete.
                        </p>
                    </div>
                    <div className="column">
                        <div className="info-box">
                            <h3 className="subtitle is-3 text-align-center">At a Glance</h3>
                            <ul className="is-size-5">
                                <li>
                                    <b>14</b> states and Puerto Rico
                                </li>
                                <li>
                                    <b>{formatNumber(dams, 0)}</b> dams
                                </li>
                                <li>
                                    <b>{formatNumber(barriers, 0)}</b> road-related barriers assessed for impact to
                                    aquatic organisms
                                </li>
                                <li>
                                    <b>{formatNumber(miles, 1)}</b> miles of connected aquatic network length, on
                                    average
                                </li>
                            </ul>
                            <img src={SARPLogo} alt="SARP Logo" style={{ marginTop: "1rem", width: "15rem", marginLeft: '1rem'}} />
                        </div>
                    </div>
                </div>
            </section>

            <section>
                <h3 className="title is-3">
                    The Southeast Aquatic Barrier Prioritization Tool empowers you with the latest inventory data.
                </h3>
                <h3 className="subtitle is-3" style={{ marginTop: "1rem" }}>
                    <i className="fas fa-chart-bar" /> Summarize the inventory across the region
                </h3>
                <div className="columns">
                    <div className="column is-two-thirds">
                        <p>
                            Explore summaries of the inventory across the region by state, county, or different levels
                            of watersheds and ecoregions.
                            <br />
                            <br />
                            These summaries are a good way to become familiar with the level of aquatic fragmentation
                            across the Southeast. Find out how many aquatic barriers have already been inventoried in
                            your area! Just remember, the inventory is a living database, and is not yet comprehensive
                            across the region.
                            <br />
                            <br />
                            <Link to="/summary">
                                <button className="button is-info is-medium" type="button">
                                    <i className="fas fa-chart-bar" />
                                    &nbsp; Start summarizing
                                </button>
                            </Link>
                        </p>
                    </div>
                    <div className="column">
                        <Link to="/summary">
                            <img src={summarizeImage} alt="Summary View" />
                        </Link>
                    </div>
                </div>
            </section>

            <section>
                <h3 className="subtitle is-3">
                    <i className="fas fa-search-location" /> Prioritize aquatic barriers for removal
                </h3>
                <div className="columns">
                    <div className="column is-two-thirds">
                        <p>
                            Identify barriers for further investigation based on the criteria that matter to you.
                            <br />
                            <br />
                            You can select specific geographic areas for prioritization, including counties, states,
                            watersheds, and ecoregions. You can filter the available barriers based on criteria such as
                            likely feasibility for removal, height, and more. Once you have prioritized aquatic
                            barriers, you can download a CSV file for further analysis.
                            <br />
                            <br />
                            <Link to="/priority">
                                <button className="button is-info is-medium" type="button">
                                    <i className="fas fa-search-location" />
                                    &nbsp; Start prioritizing
                                </button>
                            </Link>
                        </p>
                    </div>
                    <div className="column">
                        <Link to="/priority">
                            <img src={prioritizeImage} alt="Priority View" />
                        </Link>
                    </div>
                </div>
            </section>
        </React.Fragment>
    )
}

export default Intro
