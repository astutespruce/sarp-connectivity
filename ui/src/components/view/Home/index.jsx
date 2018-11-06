import React from "react"
// import PropTypes from 'prop-types'
import { Link } from "react-router-dom"

import Section from "./Section"

import { ReactComponent as HighSinuosityIcon } from "../../../img/sinuosity_high.svg"
import { ReactComponent as LowSinuosityIcon } from "../../../img/sinuosity_low.svg"
import { ReactComponent as HighSizeClassesIcon } from "../../../img/size_classes_high.svg"
import { ReactComponent as LowSizeClassesIcon } from "../../../img/size_classes_low.svg"

import SARPLogo from "../../../img/sarp_logo.png"
import CBILogo from "../../../img/cbi_logo.png"
import FishImage from "../../../img/iStock-181890680.jpg"

// Photo by American Public Power Association on Unsplash, https://unsplash.com/photos/FUeb2npsblQ
import DamImage from "../../../img/american-public-power-association-430861-unsplash.jpg"

// Photo by Robert Zunikoff on Unsplash, https://unsplash.com/photos/ko7Tp_LyAt4
import WaterStonesImage from "../../../img/robert-zunikoff-409755-unsplash.jpg"

const Home = () => (
    <div id="Home" className="view">
        <Section
            id="HomeHeader"
            image={FishImage}
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
            </p>
        </Section>
        <Section image={DamImage} dark title="The Southeast Aquatic Barrier Inventory">
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
        <Section title="How are aquatic barriers prioritized for removal?">
            <p>
                In order to prioritize dams for removal, first they need to be evaluated according to different
                criteria:
            </p>
            <div>
                <section>
                    <h3 className="is-size-3 flex-container flex-align-center">
                        <HighSinuosityIcon />
                        <div>Network sinuosity</div>
                    </h3>
                    <p>
                        Network sinuosity is a measure of how much the path of the river or stream deviates from a
                        straight line. First, the amount of curvature of each upstream segment from a barrier is
                        calculated. These measures are then averaged together based on the length of each segment, so
                        that longer segments contribute more to the overall measure for the upstream network.
                        <br />
                        <br />
                        In general, rivers and streams that are more sinuous generally indicate those that have lower
                        alteration from human disturbance such as channelization and diking, whereas rivers that have
                        been extensively tend to be less sinous.
                    </p>
                    <div className="prioritization-details flex-container flex-justify-space-between">
                        <div>
                            <HighSinuosityIcon />
                            <h4 className="is-size-4 text-align-center">High Sinuosity</h4>
                            <p>
                                Rivers and streams with high sinuosity are likely less altered by artificial
                                channelization, and may have a wider variety of in-stream habitats...
                            </p>
                        </div>
                        <div>
                            <LowSinuosityIcon />
                            <h4 className="is-size-4 text-align-center">Low Sinuosity</h4>
                            <p>
                                Rivers and streams with lower sinuosity may be more altered by artificial
                                channelization...
                            </p>
                        </div>
                    </div>
                </section>

                <section>
                    <h3 className="is-size-3 flex-container flex-align-center">
                        <HighSizeClassesIcon />
                        <div>Number of size classes gained</div>
                    </h3>
                    <p>
                        A barrier that has tributaries upstream with different sizes, such as small streams and rivers,
                        would contribute a higher number of size classes to the network if it is removed. In contrast, a
                        barrier that has another barrier immediately upstream, with no additional tributaries in
                        between, does not contribute any additional size classes to the network.
                        <br />
                        <br />
                        In general, a barrier that has a more complex upstream network will provide bigger gains for
                        restoring aquatic connectivity.
                    </p>
                    <div className="prioritization-details flex-container flex-justify-space-between">
                        <div>
                            <HighSizeClassesIcon />
                            <h4 className="is-size-4 text-align-center">More size classes gained</h4>
                            <p>Dams that have several size classes upstream are ...</p>
                        </div>
                        <div>
                            <LowSizeClassesIcon />
                            <h4 className="is-size-4 text-align-center">No size classes gained</h4>
                            <p>Dams that do not contribute any additional size classes are...</p>
                        </div>
                    </div>
                </section>

                <section />
            </div>
            <p>
                <br />
                <br />
                <br />
                Not all dams have this information, and therefore cannot be prioritized at this time.
            </p>
        </Section>
        <Section title="Example use case: regional planning">
            <p>
                You can also use this tool to better understand the number and location of aquatic barriers across the
                southeastern U.S. You can use this information to guide regional planning and allocate resources
                targeted at improving aquatic conditions. You can use this information to help stakeholders and others
                understand the impact of aquatic barriers across the region, and build awareness about how to reduce
                those impacts…
            </p>
        </Section>
        <Section image={WaterStonesImage} dark title="Example use case: removing small, unneeded dams on private land">
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

        <Section title="The Southeast Aquatic Resources Partnership">
            <div className="columns">
                <div className="column is-two-thirds">
                    <p>
                        The{" "}
                        <a href="https://southeastaquatics.net/" target="_blank" rel="noopener noreferrer">
                            Southeast Aquatic Resources Partnership
                        </a>
                        &nbsp; (SARP) is a regional collaboration of natural resource and science agencies, conservation
                        organizations and private interests developed to strengthen the management and conservation of
                        aquatic resources in the southeastern United States.
                    </p>
                </div>
                <div className="column">
                    <img src={SARPLogo} style={{ width: "100%" }} alt="SARP logo" />
                </div>
            </div>
            <p>
                Nationally, SARP works to implement the goals of the National Fish Habitat Action Plan in some of the
                United States most ecologically and economically significant watersheds. Regionally, SARP works with
                partners in 14 states in the Southeast to conduct science-based watershed and habitat assessments that
                collectively identify regional conservation priorities. SARP works with communities to facilitate
                locally-driven conservation projects that bring together partners and funding to help meet regional
                priorities.
                <br />
                <br />
                SARP and partners have been working to build a community of practice surrounding barrier removal through
                the development of state-based Aquatic Connectivity Teams (ACTs). These teams create a forum that allows
                resource managers from all sectors to work together and share resources, disseminate information, and
                examine regulatory streamlining processes as well as project management tips and techniques. These teams
                are active in Arkansas, Florida, Georgia, North Carolina, and Tennessee.
            </p>
        </Section>

        <Section id="HomeFooter">
            <div className="columns">
                <div className="column is-two-thirds">
                    <p className="is-size-7">
                        This application was created by the&nbsp;
                        <a href="https://consbio.org" target="_blank" rel="noopener noreferrer">
                            Conservation Biology Institute
                        </a>
                        &nbsp; (CBI) in partnership with the&nbsp;
                        <a href="https://southeastaquatics.net/" target="_blank" rel="noopener noreferrer">
                            Southeast Aquatic Resources Partnership
                        </a>
                        . CBI provides science and software development to support the conservation of biodiversity.
                    </p>
                </div>
                <div className="column">
                    <img src={CBILogo} style={{ height: 48 }} alt="CBI logo" />
                </div>
            </div>
        </Section>
    </div>
)

Home.propTypes = {}

export default Home
