import React from "react"
import { Link } from "react-router-dom"

import { formatNumber } from "../../../utils/format"

import summaryStats from "../../../data/summary_stats.json"
import summarizeImage from "../../../img/summarize.jpg"
import prioritizeImage from "../../../img/prioritize.jpg"
import fishImage from "../../../img/iStock-181890680.jpg"

const { dams, barriers, miles } = summaryStats.southeast

function Intro() {
    return (
        <React.Fragment>
            <div className="image-header" style={{ backgroundImage: `url(${fishImage})` }} />
            <div className="container page-header">
                <h1 className="title is-1 is-large">Aquatic connectivity is essential.</h1>
                <h3 className="subtitle is-3 is-large">
                    Fish and other aquatic organisms depend on high quality, connected river networks.
                </h3>
                <section>
                    <p className="is-size-4">
                        A legacy of human use of river networks have left them fragmented by barriers such as dams and
                        culverts. Fragmentation prevents species from dispersing and accessing habitats required for
                        their persistence through changing conditions.
                        <br />
                        <br />
                        Recently improved inventories of aquatic barriers enable us to describe, understand, and
                        prioritize them for removal, restoration, and mitigation. Through this tool and others, we
                        empower you by providing information on documented barriers and standardized methods by which to
                        prioritize barriers of interest for restoration efforts.
                    </p>
                </section>

                <section>
                    <h3 className="title is-3">The Southeast Aquatic Barrier Inventory:</h3>
                    <div className="columns">
                        <div className="column is-two-thirds">
                            <p>
                                This inventory is a growing and living database of dams, culverts, and other road
                                crossings compiled by the Southeast Aquatic Resources Partnership with the generous
                                support from many partners and funders. Information about network connectivity,
                                landscape condition, and presence of threatened and endangered aquatic organisms are
                                added to this inventory to help you investigate barriers at any scale for your desired
                                purposes.
                                <br />
                                <br />
                                This inventory consists of datasets from local, state, and federal partners. It is
                                supplemented with input from partners with on the ground knowledge of specific
                                structures. The information on barriers is not complete or comprehensive across the
                                region, and depends on the availability and completeness of existing data and level of
                                partner feedback. Some areas of the region are more complete than others but none should
                                be considered 100% complete.
                                <br />
                                <br />
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
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <h3 className="title is-3">
                        The Southeast Aquatic Barrier Prioritization Tool empowers you with the latest inventory data:
                    </h3>
                    <h3 className="subtitle is-3 no-margin">
                        <Link to="/summary">
                            <i className="fas fa-chart-bar" /> Summarize
                        </Link>
                    </h3>
                    <div className="columns">
                        <div className="column is-two-thirds">
                            <p>
                                Explore summaries of the inventory across the region by state, county, or different
                                levels of watersheds and ecoregions.
                                <br />
                                <br />
                                These summaries are a good way to become familiar with the level of aquatic
                                fragmentation across the Southeast. Find out how many aquatic barriers have already been
                                inventoried in your area! Just remember, the inventory is a living database, and is not
                                yet comprehensive across the region.
                                <br />
                                <br />
                                <Link to="/summary">Start exploring summary information...</Link>
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
                    <h3 className="subtitle is-3 no-margin">
                        <Link to="/priority">
                            <i className="fas fa-search-location" /> Prioritize
                        </Link>
                    </h3>
                    <div className="columns">
                        <div className="column is-two-thirds">
                            <p>
                                Identify barriers for further investigation based on the criteria that matter to you.
                                <br />
                                <br />
                                You can select specific geographic areas for prioritization, including counties, states,
                                watersheds, and ecoregions. You can filter the available barriers based on criteria such
                                as likely feasibility for removal, height, and more. Once you have prioritized aquatic
                                barriers, you can download a CSV file for further analysis.
                                <br />
                                <br />
                                <Link to="/priority">Start prioritizing aquatic barriers for removal...</Link>
                            </p>
                        </div>
                        <div className="column">
                            <Link to="/priority">
                                <img src={prioritizeImage} alt="Priority View" />
                            </Link>
                        </div>
                    </div>
                </section>

                <section>
                    <div className="columns">
                        <div className="column is-two-thirds">
                            <h3 className="title is-3" style={{ marginBottom: 0 }}>
                                Get involved!
                            </h3>
                            <p>
                                You can help improve the inventory by sharing data, assisting with field reconnaissance
                                to evaluate the impact of aquatic barriers, joining an{" "}
                                <Link to="/teams">Aquatic Connectivity Team</Link>, or even by reporting issues with the
                                inventory data in this tool.
                                <br />
                                <br />
                                <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn more about how you
                                can help improve aquatic connectivity in the Southeast.
                            </p>
                        </div>
                        <div className="column">
                            <h3 className="title is-3 no-margin">Need Help?</h3>
                            <p>
                                If you are not able to get what you need from this tool or if you need to report an
                                issue, please&nbsp;
                                <a href="mailto:kat@southeastaquatics.net">let us know</a>!
                            </p>
                        </div>
                    </div>
                </section>
            </div>
        </React.Fragment>
    )
}

export default Intro
