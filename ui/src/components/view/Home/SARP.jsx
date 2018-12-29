import React from "react"
import { Link } from "react-router-dom"
import Section from "../../Section"

import SARPLogo from "../../../img/sarp_logo.png"
import GeorgiaACTImage from "../../../img/GA_ACT.jpg"

// From https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/
import ForestStream from "../../../img/6882770647_60c0d68a9c_z.jpg"

function SARP() {
    return (
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
            <div className="columns" style={{ marginTop: "2rem" }}>
                <div className="column">
                    <img src={ForestStream} alt="Stream" className="photo" />
                    <div className="is-size-7 has-text-grey">
                        Photo:{" "}
                        <a
                            href="https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Sam D. Hamilton Noxubee National Wildlife Refuge in Mississippi, USFWS
                        </a>
                        .
                    </div>
                </div>
                <div className="column is-two-thirds">
                    <p>
                        SARP works with partners to protect, conserve, and restore aquatic resources including habitats
                        throughout the Southeast for the continuing benefit, use, and enjoyment of the American people.
                        SARP is also one of the first Fish Habitat Partnerships under the the National Fish Habitat
                        Partnership umbrella that works to conserve and protect the nation’s fisheries and aquatic
                        systems through a network of 20 Fish Habitat Partnerships.
                    </p>
                </div>
            </div>
            <div className="columns" style={{ marginTop: "2rem" }}>
                <div className="column is-two-thirds">
                    <p>
                        SARP and partners have been working to build a community of practice surrounding barrier removal
                        through the development of state-based Aquatic Connectivity Teams (ACTs). These teams create a
                        forum that allows resource managers from all sectors to work together and share resources,
                        disseminate information, and examine regulatory streamlining processes as well as project
                        management tips and techniques. These teams are active in Arkansas, Florida, Georgia, North
                        Carolina, and Tennessee.
                        <br />
                        <br />
                        <Link to="/teams">Learn more about aquatic connectivity teams.</Link>
                    </p>
                </div>
                <div className="column">
                    <img src={GeorgiaACTImage} alt="Georgia Aquatic Connectivity Team" className="photo" />
                    <div className="is-size-7 has-text-grey">
                        Photo:{" "}
                        <a
                            href="https://www.southeastaquatics.net/news/white-dam-removal-motivates-georgia-conservation-practitioners"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            Georgia Aquatic Connectivity Team
                        </a>
                        .
                    </div>
                </div>
            </div>
        </Section>
    )
}

export default SARP
