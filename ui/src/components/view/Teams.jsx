import React, { useEffect } from "react"

import { scrollIntoView } from "../../utils/dom"
// import Section from "../Section"

import { CONNECTIVITY_TEAMS } from "../../constants"

// from SARP
import headerImage from "../../img/TN_ACT2.jpg"

// from SARP
import peopleCulvertImage from "../../img/IMG_1530.jpg"

// from: https://www.southeastaquatics.net/news/white-dam-removal-motivates-georgia-conservation-practitioners
import GeorgiaACTImage from "../../img/GA_ACT.jpg"

// from: https://www.southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap/connectivity-teams/arkansas-stream-heritage-partnership/copy_of_ArkansasWorkshop.jpg/view
import ArkansasACTImage from "../../img/AR_ACT.jpg"

// from SARP
import TennesseeACTImage from "../../img/TN_ACT.jpg"

const teamImages = {
    Arkansas: {
        image: ArkansasACTImage,
        credits: "Kat Hoenke, Southeast Aquatic Resources Partnership"
    },
    Georgia: {
        image: GeorgiaACTImage
    },
    Tennessee: {
        image: TennesseeACTImage,
        credits: "Jessica Graham, Southeast Aquatic Resources Partnership"
    }
}

function Teams() {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })

    return (
        <div id="ContentPage">
            <div className="image-header" style={{ backgroundImage: `url(${headerImage})` }}>
                <div className="credits">Photo credit: Jessica Graham, Southeast Aquatic Resources Partnership.</div>
            </div>

            <div className="container">
                <h1 className="title is-1">Aquatic Connectivity Teams</h1>
                {Object.entries(CONNECTIVITY_TEAMS).map(([state, team], i) => (
                    <React.Fragment key={state}>
                        {i > 0 ? <div className="divider" /> : null}

                        <section>
                            <h3 className="title is-3">{state}</h3>
                            <p>
                                {team.description}
                                <br />
                                <br />
                                For more information, please contact{" "}
                                <a href={`mailto:${team.contact.email}`}>{team.contact.name}</a>.
                            </p>
                            {teamImages[state] ? (
                                <React.Fragment>
                                    <img
                                        src={teamImages[state].image}
                                        alt={`${state} Aquatic Connectivity Team`}
                                        style={{ marginTop: "2rem" }}
                                    />
                                    {teamImages[state].credits ? (
                                        <div className="has-text-grey is-size-7 text-align-right">
                                            Photo: {teamImages[state].credits}
                                        </div>
                                    ) : null}
                                </React.Fragment>
                            ) : null}
                        </section>
                    </React.Fragment>
                ))}
                <section>
                    <p>
                        For more information about Aquatic Connectivity Teams, please see the{" "}
                        <a
                            href="https://www.southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap/connectivity-teams"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            SARP Aquatic Connectivity Teams page
                        </a>
                        .<br />
                        <br />
                    </p>
                    <img src={peopleCulvertImage} alt="Culvert evaluation" />
                    <div className="has-text-grey is-size-7 text-align-right">
                        Photo: Jessica Graham, Southeast Aquatic Resources Partnership
                    </div>
                </section>
            </div>
        </div>
    )
}

export default Teams
