import React, { useEffect } from "react"

import { scrollIntoView } from "../../utils/dom"
// import Section from "../Section"

import { CONNECTIVITY_TEAMS } from "../../constants"

// https://www.flickr.com/photos/usfwssoutheast/10696646974/in/album-72157637310346925/
// import headerImage from "../../img/10696646974_748f57553f_k.jpg"

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
    Arkansas: ArkansasACTImage,
    Georgia: GeorgiaACTImage,
    Tennessee: TennesseeACTImage
}

function Teams() {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })

    return (
        <div id="ContentPage" className="subpage">
            <div className="image-header" style={{ backgroundImage: `url(${headerImage})` }} />

            <div className="container">
                <h1 className="title is-1">Aquatic Connectivity Teams</h1>
                {Object.entries(CONNECTIVITY_TEAMS).map(([state, team]) => (
                    <section key={state}>
                        <h3 className="title is-3">{state}</h3>
                        <p>
                            {team.description}
                            <br />
                            <br />
                            For more information, please contact{" "}
                            <a href={`mailto:${team.contact.email}`}>{team.contact.name}</a>.
                        </p>
                        {teamImages[state] ? (
                            <img
                                src={teamImages[state]}
                                alt={`${state} Aquatic Connectivity Team`}
                                style={{ marginTop: "2rem" }}
                            />
                        ) : null}
                    </section>
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
                </section>
            </div>
        </div>
    )
}

export default Teams
