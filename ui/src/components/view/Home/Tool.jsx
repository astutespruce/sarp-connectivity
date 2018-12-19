import React from "react"
import { Link } from "react-router-dom"

import Section from "../../Section"

function Tool() {
    return (
        <Section title="The Southeast Aquatic Barrier Prioritization Tool">
            <p>
                Using this tool, you can:
                <br />
                <Link to="/summary">
                    <b>Summarize</b>
                </Link>
                &nbsp; the inventory across the region using different levels of watersheds and ecoregions. [screenshot
                of regional summary view to the right]
                <br />
                <br />
                <Link to="/priority">
                    <b>Prioritize</b>
                </Link>
                &nbsp; barriers for further investigation based on the criteria that matter to you. [screenshot of
                filters sidebar of prioritization view to the right]
                <br />
                <br />
            </p>
            <h4 className="title is-5" style={{ marginBottom: 0 }}>
                Need Help?
            </h4>
            <p>
                If you are not able to get what you need from this tool, or if you need to report an issue, please&nbsp;
                <a href="mailto:kat@southeastaquatics.net">contact us</a>!
            </p>
        </Section>
    )
}

export default Tool
