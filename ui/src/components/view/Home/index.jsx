import React from "react"
// import PropTypes from 'prop-types'
import { Link } from "react-router-dom"

import Section from "./Section"
import Image1 from "../../../img/iStock-181890680.jpg"
import Image2 from "../../../img/IMG_1530.jpg"

const Home = () => (
    <div id="Home" className="view">
        <Section
            id="HomeHeader"
            image={Image1}
            dark
            title="Fish and other aquatic organisms"
            subtitle="depend on high quality, connected river networks."
        >
            <p>
                A legacy of human use of these networks have left them fragmented by barriers such as dams and culverts.
                Species are no longer able to disperse effectively through their native range, which impacts the
                persistence of threatened and game fish species and many other aquatic organisms.
            </p>
            <p>
                Recently improved inventories of aquatic barriers enable us to describe, understand, and prioritize them
                for removal, restoration, and mitigation. Through this tool and others, we intend to empower you to…
            </p>
            <p>
                This tool empowers you to explore the growing inventory of dams and road / stream crossings across the
                southeast U.S.
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
                                    <h4 className="is-size-4">View summaries</h4>
                                </div>
                            </div>
                        </div>
                        <p>Explore summaries of small and large aquatic barriers across the southeast.</p>
                        <div className="has-text-centered is-size-5">
                            <Link to="/compare" style={{ color: "#3273dc" }}>
                                Start comparing
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
                                    <h4 className="is-size-4">Calculate priorities</h4>
                                </div>
                            </div>
                        </div>
                        <p>Prioritize aquatic barriers for removal in your area of interest.</p>
                        <div className="has-text-centered is-size-5">
                            <Link to="/explore" style={{ color: "#3273dc" }}>
                                {" "}
                                Start exploring
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

        <Section title="The Southeast Aquatic Barrier Inventory Visualization Tool">
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
            </p>
        </Section>
        <Section image={Image2} dark title="The Southeast Aquatic Barrier Inventory">
            <p>
                This inventory is a growing database of dams and road / stream crossings compiled by the Southeast
                Aquatic Resources Partnership and partners. Information about network analysis, landscape condition, and
                presence of threatened aquatic organisms are added to this inventory to help you… [description of key
                attributes of inventory, possibly with links or popups for more information about each. E.g., define /
                explain absolute miles gained, sinuosity, etc] [brief description of status / completeness of inventory
                to help people understand that inventory is not complete, and is particularly spotty for some states /
                areas]
            </p>
        </Section>
        <Section title="Example use case: removing small, unneeded dams on private land">
            <p>
                One way you can use this tool is to identify and prioritize dams according to the criteria that matter
                to you. For example, you can first select the dams that are within the watersheds where you work. Then
                you can filter those dams further to find those that have a low height, are on private land, and were
                constructed a long time ago. These dams may no longer be necessary, but since they haven’t been targeted
                for removal, they may remain barriers within the aquatic network. Once you’ve selected the dams that
                meet your criteria, you can re-prioritize these to find those that would contribute most to restoring
                overall aquatic connectivity. You can explore these further using the interactive map, or you can export
                them to a spreadsheet for further analysis and exploration. You can use this information to supplement
                your grant proposals and work plans to…
            </p>
        </Section>

        <Section dark title="Example use case: regional planning">
            <p>
                You can also use this tool to better understand the number and location of aquatic barriers across the
                southeastern U.S. You can use this information to guide regional planning and allocate resources
                targeted at improving aquatic conditions. You can use this information to help stakeholders and others
                understand the impact of aquatic barriers across the region, and build awareness about how to reduce
                those impacts…
            </p>
        </Section>

        <Section title="The Southeast Aquatic Resources Partnership">TODO</Section>

        <Section subtitle="The Conservation Biology Institute">TODO</Section>
    </div>
)

Home.propTypes = {}

export default Home
