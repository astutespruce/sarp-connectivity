import React from "react"
import { Link } from "react-router-dom"

import Section from "../../Section"

import SummarizeImage from "../../../img/summarize.jpg"
import PrioritizeImage from "../../../img/prioritize.jpg"

function Tool() {
    return (
        <Section title="The Southeast Aquatic Barrier Prioritization Tool">
            <h5 className="subtitle is-4">Using this tool, you can:</h5>
            <div className="columns">
                <div className="column">
                    <p>
                        <Link to="/summary">
                            <b>Summarize</b>
                        </Link>
                        &nbsp; the inventory across the region by state, county, or different levels of watersheds and
                        ecoregions.
                        <br />
                        <br />
                        These summaries are a good way to become familiar with the level of aquatic fragmentation across
                        the Southeast. Find out how many aquatic barriers have already been inventoried in your area!
                        Just remember, the inventory is a living database, and is not yet comprehensive across the
                        region.
                    </p>
                </div>
                <div className="column">
                    <img src={SummarizeImage} alt="Summary View" />
                </div>
            </div>

            <div className="columns" style={{ marginTop: "2rem" }}>
                <div className="column">
                    <p>
                        <Link to="/priority">
                            <b>Prioritize</b>
                        </Link>
                        &nbsp; barriers for further investigation based on the criteria that matter to you.
                        <br />
                        <br />
                        You can select specific geographic areas for prioritization, including counties, states,
                        watersheds, and ecoregions. You can filter the available barriers based on criteria such as
                        likely feasibility for removal, height, and more. Once you have prioritized aquatic barriers,
                        you can download a CSV file for further analysis.
                    </p>
                </div>
                <div className="column">
                    <img src={PrioritizeImage} alt="Priority View" />
                </div>
            </div>
            <div>
                <h4 className="title is-5" style={{ marginBottom: 0 }}>
                    Need Help?
                </h4>
                <p>
                    If you are not able to get what you need from this tool, or if you need to report an issue,
                    please&nbsp;
                    <a href="mailto:kat@southeastaquatics.net">contact us</a>!
                </p>
            </div>
        </Section>
    )
}

export default Tool
