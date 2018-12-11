import React from "react"
// import PropTypes from 'prop-types'
import { Link } from "react-router-dom"

import { scrollIntoView } from "../../../utils/dom"

import Section from "./Section"

import { ReactComponent as HighSinuosityIcon } from "../../../img/sinuosity_high.svg"
import { ReactComponent as LowSinuosityIcon } from "../../../img/sinuosity_low.svg"
import { ReactComponent as HighSizeClassesIcon } from "../../../img/size_classes_high.svg"
import { ReactComponent as LowSizeClassesIcon } from "../../../img/size_classes_low.svg"
import { ReactComponent as HighLengthIcon } from "../../../img/length_high.svg"
import { ReactComponent as LowLengthIcon } from "../../../img/length_low.svg"
import { ReactComponent as HighLandcoverIcon } from "../../../img/nat_landcover_high.svg"
import { ReactComponent as LowLandcoverIcon } from "../../../img/nat_landcover_low.svg"
import { ReactComponent as FunctionalNetwork } from "../../../img/functional_network.svg"

import SARPLogo from "../../../img/sarp_logo.png"
import CBILogo from "../../../img/cbi_logo.png"
import FishImage from "../../../img/iStock-181890680.jpg"

// Photo by American Public Power Association on Unsplash, https://unsplash.com/photos/FUeb2npsblQ
import DamImage from "../../../img/american-public-power-association-430861-unsplash.jpg"

// Photo from: https://www.flickr.com/photos/savannahcorps/9272554306/
import DamImage2 from "../../../img/9272554306_b34bf886f4_z.jpg"

// Photo from: https://unsplash.com/photos/FAs7023dS34
import DamImage3 from "../../../img/alain-rieder-998811-unsplash.jpg"

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
                A legacy of human use of river networks have left them fragmented by barriers such as dams and culverts.
                Fragmentation prevents species from dispersing and accessing habitats required for their persistence
                through changing conditions.
            </p>
            <p>
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
                If you are not able to get what you need from this tool, or if you need to report an issue, please{" "}
                <a href="mailto:kat@southeastaquatics.net">contact us</a>!
            </p>
        </Section>
        <Section image={DamImage} dark title="The Southeast Aquatic Barrier Inventory">
            <p>
                This inventory is a growing and living database of dams and road / stream crossings compiled by the
                Southeast Aquatic Resources Partnership with the generous support from many partners and funders.
                Information about network connectivity, landscape condition, and presence of threatened and endangered
                aquatic organisms are added to this inventory to help you investigate barriers at any scale for your
                desired purposes.
                <br />
                <br />
                This inventory consists of datasets from local, state, and federal partners, along with input from
                various partners with on the ground knowledge of specific structures. The information on barriers is not
                complete and dependent upon the availability and completion of data. Some areas of the region are more
                complete than others but none should be considered 100% complete.
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

        <Section title="Key Concept: Aquatic Barriers">
            <div className="columns">
                <div className="column">
                    <p>
                        These barriers are natural and human-made structures that impede the passage of aquatic
                        organisms through the river network. Some human-made barriers may no longer serve their original
                        purpose and have fallen into disrepair. These barriers may be particularly good candidates for
                        removal or remediation to restore aquatic connectivity.
                        <br />
                        <br />
                        Aquatic barriers include:
                    </p>
                    <ul>
                        <li>Waterfalls (from the USGS Waterfalls Inventory)</li>
                        <li>Dams</li>
                        <li>Small barriers (culverts and similar)</li>
                    </ul>
                    <p>
                        <br />
                        Not all barriers completely block the passage of all aquatic organisms. However, in this tool
                        waterfalls and dams are considered &quot;hard&quot; barriers that divide the aquatic network.
                        <br />
                        <br />
                        Small barriers are analyzed somewhat independently of waterfalls and dams: the location of small
                        barriers does not affect the prioritization of dams, but the location of dams <i>does</i> affect
                        the prioritization of small barriers.
                    </p>
                </div>
                <div className="column">
                    <img src={DamImage3} alt="" className="photo" />
                    <img src={DamImage2} alt="Hartwell Dam" className="photo" style={{ marginTop: "3rem" }} />
                </div>
            </div>
        </Section>
        <Section title="Key Concept: Functional Networks">
            <div className="columns">
                <div className="column is-two-thirds">
                    <p>
                        Functional networks are the stream and river reaches that extend upstream from a barrier or
                        river mouth to either the origin of that stream or the next upstream barrier. They form the
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
                        &nbsp; (NHDPlus) for all areas except the lower Mississipi (hydrologic region 8), where the
                        NHDPlus Medium Resolution version was the only one available. Where possible, their locations
                        were manually inspected to verify their correct position on the aquatic network.
                        <br />
                        <br />
                        <span className="icon">
                            <i className="fas fa-exclamation-triangle" />
                        </span>
                        Note: due to limitations of existing data sources for aquatic networks, not all aquatic barriers
                        can be correctly located on the aquatic networks. These barriers are not included in the network
                        connectivity analysis and cannot be prioritized using this tool. However, these data can still
                        be downloaded from this tool and used for offline analysis.
                    </p>
                </div>
                <div className="column">
                    <FunctionalNetwork style={{ height: "30rem" }} />
                </div>
            </div>
        </Section>
        <Section title="How are aquatic barriers prioritized for removal?">
            <section>
                <p>
                    In order to prioritize dams for removal, they are first characterized based on particular metrics of
                    their functional networks:
                </p>
                <ul>
                    <li>
                        <a onClick={() => scrollIntoView("NetworkLengthDef")}>Network length</a>
                    </li>
                    <li>
                        <a onClick={() => scrollIntoView("NetworkSinuosityDef")}>Network sinuosity</a>
                    </li>
                    <li>
                        <a onClick={() => scrollIntoView("NetworkComplexityDef")}>Network complexity</a>
                    </li>
                    <li>
                        <a onClick={() => scrollIntoView("NaturalLandcoverDef")}>Floodplain natural landcover</a>
                    </li>
                </ul>

                <p>
                    <br />
                    <br />
                    These metrics are then combined to create three scenarios for prioritizing barriers for removal:
                </p>
                <ul>
                    <li>
                        <a onClick={() => scrollIntoView("NetworkConnectivityDef")}>Network connectivity</a>
                    </li>
                    <li>
                        <a onClick={() => scrollIntoView("WatershedConditionDef")}>Watershed condition</a>
                    </li>
                    <li>
                        <a onClick={() => scrollIntoView("CombinedScoreDef")}>
                            Network connectivity and watershed condition
                        </a>
                    </li>
                </ul>
                <br />
                <br />
                <p>TODO: explain the scoring approach</p>
                <p>Using this tool, you can select the scenario that best meets your needs.</p>
            </section>
            <section>
                <h3 id="NetworkLengthDef" className="is-size-3 flex-container flex-align-center">
                    <HighLengthIcon />
                    <div>Metric: network length</div>
                </h3>
                <p>
                    Network length measures the amount of connected aquatic network length that would be added to the
                    network by removing the barrier. It is the smaller of either the total upstream network length or
                    total downstream network length for the networks subdivided by this barrier. This is because a
                    barrier may have a very large upstream network, but if there is another barrier immediately
                    downstream, the overall effect of removing this barrier will be quite small.
                </p>
                <div className="prioritization-details flex-container flex-justify-space-between">
                    <div>
                        <HighLengthIcon />
                        <h4 className="is-size-4 text-align-center">High Network Length</h4>
                        <p>
                            Barriers that have large upstream and downstream networks will contribute a large amount of
                            connected aquatic network length if they are removed.
                        </p>
                    </div>
                    <div>
                        <LowLengthIcon />
                        <h4 className="is-size-4 text-align-center">Low Network Length</h4>
                        <p>
                            Barriers that have small upstream or downstream networks contribute relatively little
                            connected aquatic network length if removed.
                        </p>
                    </div>
                </div>
                <h5 className="title is-5">Methods:</h5>
                <ol>
                    <li>
                        The total upstream length is calculated as the sum of the lengths of all upstream river and
                        stream reaches.
                    </li>
                    <li>
                        The total downstream length is calculated for the network immediately downstream of the barrier.
                        Note: this is the total network length of the downstream network, <i>not</i> the shortest
                        downstream path to the next barrier or river mouth.
                    </li>
                    <li>Network length is the smaller of the upstream or downstream network lengths.</li>
                </ol>
            </section>
            <section>
                <h3 id="NetworkSinuosityDef" className="is-size-3 flex-container flex-align-center">
                    <HighSinuosityIcon />
                    <div>Metric: network sinuosity</div>
                </h3>
                <p>
                    Network sinuosity is a measure of how much the path of the river or stream deviates from a straight
                    line. In general, rivers and streams that are more sinuous generally indicate those that have lower
                    alteration from human disturbance such as channelization and diking, whereas rivers that have been
                    extensively altered tend to be less sinous.
                </p>
                <div className="prioritization-details flex-container flex-justify-space-between">
                    <div>
                        <HighSinuosityIcon />
                        <h4 className="is-size-4 text-align-center">High Sinuosity</h4>
                        <p>
                            Rivers and streams with high sinuosity are likely less altered by artificial channelization
                            and may have a wider variety of in-stream habitat. Barriers with more sinuous upstream
                            networks may contribute more natural habitat if removed.
                        </p>
                    </div>
                    <div>
                        <LowSinuosityIcon />
                        <h4 className="is-size-4 text-align-center">Low Sinuosity</h4>
                        <p>
                            Rivers and streams with lower sinuosity may be more altered by artificial channelization and
                            may have a lower variety of in-stream habitat. Barriers with less sinuous upstream networks
                            may contribute less natural habitat if removed.
                        </p>
                    </div>
                </div>
                <h5 className="title is-5">Methods:</h5>
                <ol>
                    <li>
                        The sinuosity of each stream is calculated as the ratio between the length of that reach and the
                        straight line distance between the endpoints of that reach. The greater the total length
                        compared to the straight line distance, the higher the sinuosity.
                    </li>
                    <li>
                        Reaches are combined using a length-weighted average to calculate the overall sinuosity of each
                        functional network
                    </li>
                </ol>
            </section>

            <section>
                <h3 id="NetworkComplexityDef" className="is-size-3 flex-container flex-align-center">
                    <HighSizeClassesIcon />
                    <div>Metric: network complexity</div>
                </h3>
                <p>
                    A barrier that has upstream tributaries of different size classes, such as small streams, small
                    rivers, and large rivers, would contribute a more complex connected aquatic network if it was
                    removed. In contrast, a barrier with fewer upstream tributaries may contribute few if any size
                    classes to the network if removed. In general, a more complex network composed of a greater range of
                    size classes is more likely to have a wide range of available habitat for a greater number of
                    aquatic species.
                </p>
                <div className="prioritization-details flex-container flex-justify-space-between">
                    <div>
                        <HighSizeClassesIcon />
                        <h4 className="is-size-4 text-align-center">More size classes gained</h4>
                        <p>
                            Barriers that have several size classes upstream are more likely to contribute a more
                            complex network with a greater range of aquatic habitat for a greater variety of species.
                        </p>
                    </div>
                    <div>
                        <LowSizeClassesIcon />
                        <h4 className="is-size-4 text-align-center">No size classes gained</h4>
                        <p>
                            Barriers that do not contribute any additional size classes are less likely to contribute a
                            wide range of aquatic habitat.
                        </p>
                    </div>
                </div>
                <h5 className="title is-5">Methods:</h5>
                <ol>
                    <li>
                        Stream and river reaches were assigned to size classes based on total drainage area:
                        <ul>
                            <li>
                                Headwaters: &lt; 10 km
                                <sup>2</sup>
                            </li>
                            <li>
                                Creeks: &ge; 10 km
                                <sup>2</sup> and &lt; 100 km
                                <sup>2</sup>
                            </li>
                            <li>
                                Small rivers: &ge; 100 km
                                <sup>2</sup> and &lt; 518 km
                                <sup>2</sup>
                            </li>
                            <li>
                                Medium tributary rivers: &ge; 519 km
                                <sup>2</sup> and &lt; 2,590 km
                                <sup>2</sup>
                            </li>
                            <li>
                                Medium mainstem rivers: &ge; 2,590 km
                                <sup>2</sup> and &lt; 10,000 km
                                <sup>2</sup>
                            </li>
                            <li>
                                Large rivers: &ge; 10,000 km
                                <sup>2</sup> and &lt; 25,000 km
                                <sup>2</sup>
                            </li>
                            <li>
                                Great rivers: &ge; 25,000 km
                                <sup>2</sup>
                            </li>
                        </ul>
                    </li>
                    <li>
                        Each barrier is assigned the total number of unique size classes in its upstream functional
                        network.
                    </li>
                </ol>
            </section>

            <section>
                <h3 id="NaturalLandcoverDef" className="is-size-3 flex-container flex-align-center">
                    <HighLandcoverIcon />
                    <div>Metric: floodlplain natural landcover</div>
                </h3>
                <p>
                    Rivers and streams that have a greater amount of natural landcover in their floodplain are more
                    likely to have higher quality aquatic habitat. These areas may have more cool-water refugia for
                    temperature sensitive species due to shading from the overstory, and may have fewer water quality
                    issues. In contrast, rivers that have less natural landcover are more likely to be altered and have
                    impaired water quality.
                </p>
                <div className="prioritization-details flex-container flex-justify-space-between">
                    <div>
                        <HighLandcoverIcon />
                        <h4 className="is-size-4 text-align-center">High Natural Landcover</h4>
                        <p>
                            Barriers with aquatic networks that have more natural landcover are more likely to
                            contribute higher quality habitat if they are removed.
                        </p>
                    </div>
                    <div>
                        <LowLandcoverIcon />
                        <h4 className="is-size-4 text-align-center">Low Natural Landcover</h4>
                        <p>
                            Barriers with less natural landcover are less likely to contribute high quality habitat for
                            aquatic species if removed.
                        </p>
                    </div>
                </div>
                <h5 className="title is-5">Methods:</h5>
                <ol>
                    <li>Floodplains are delineated using: TODO: floodplain methods from Kat</li>
                    <li>Natural landcover is derived from ... TODO: methods from Kat... </li>
                    <li>Natural landcover is clipped to the floodplain area for analysis</li>
                    <li>
                        The contributing watershed (catchment) of each stream and river reach is extracted from the
                        NHDPlus dataset
                    </li>
                    <li>
                        The total amount of area in natural landcover and total floodplain area are tallied for each
                        functional network
                    </li>
                    <li>
                        Floodplain natural landcover is measured from the overall percent of natural landcover
                        throughout the entire functional network
                    </li>
                </ol>
            </section>

            <section>
                <h3 id="NetworkConnectivityDef" className="is-size-3">
                    Scenario: network connectivity
                </h3>
                <p>
                    The network connectivity score prioritizes barriers on the amount of overall connected network
                    length they would contribute if removed. This is calculated by ranking barriers from those that
                    contribute the most network length to the least.
                    <br />
                    <br />
                    This scenario is most useful if you are ... TODO
                </p>
            </section>

            <section>
                <h3 id="WatershedConditionDef" className="is-size-3">
                    Scenario: watershed condition
                </h3>
                <p>
                    The watershed scenario is calculated by ranking barriers based on their combined scores of network
                    sinuosity, network complexity, and amount of natural landcover in the floodplains. Each of these
                    metrics is weighted equally.
                    <br />
                    <br />
                    This scenario is most useful if you are ... TODO
                </p>
            </section>

            <section>
                <h3 id="CombinedScoreDef" className="is-size-3">
                    Scenario: network connectivity and watershed condition
                </h3>
                <p>
                    This scenario combines the network connectivity and watershed condition scores into a single score.
                    Network connectivity and watershed condition are weighted equally relative to each other.
                    <br />
                    <br />
                    This scenario is most useful if you are ... TODO
                </p>
            </section>
        </Section>

        <Section title="The Southeast Aquatic Resources Partnership">
            <div className="columns">
                <div className="column is-two-thirds">
                    <p>
                        The&nbsp;
                        <a href="https://southeastaquatics.net/" target="_blank" rel="noopener noreferrer">
                            Southeast Aquatic Resources Partnership
                        </a>
                        &nbsp; (SARP) was formed by the Southeastern Association of Fish and Wildlife Agencies (SEAFWA)
                        to protect aquatic resources across political boundaries as many of our river systems cross
                        multiple jurisdictional boundaries.
                    </p>
                </div>
                <div className="column">
                    <img src={SARPLogo} style={{ width: "100%" }} alt="SARP logo" />
                </div>
            </div>
            <p>
                SARP works with partners to protect, conserve, and restore aquatic resources including habitats
                throughout the Southeast for the continuing benefit, use, and enjoyment of the American people. SARP is
                also one of the first Fish Habitat Partnerships under the the National Fish Habitat Partnership umbrella
                that works to conserve and protect the nation’s fisheries and aquatic systems.
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
                    <p>
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
            <p>
                This project was supported in part by a grant from the&nbsp;
                <a href="https://www.fws.gov/fisheries/fish-passage.html" target="_blank" rel="noopener noreferrer">
                    U.S. Fish and Wildlife Service Fish Passage Program
                </a>
                .
            </p>
        </Section>
    </div>
)

Home.propTypes = {}

export default Home
