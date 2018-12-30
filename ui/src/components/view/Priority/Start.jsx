import React, { useEffect } from "react"
import PropTypes from "prop-types"

// import Section from "../../Section"
import { scrollIntoView } from "../../../utils/dom"

import damImage from "../../../img/american-public-power-association-430861-unsplash.jpg"

const Start = ({ setType }) => {
    useEffect(() => {
        scrollIntoView("ContentPage")
    })
    return (
        <div id="ContentPage">
            <div className="image-header" style={{ backgroundImage: `url(${damImage})` }}>
                <div className="credits">
                    Photo credit:{" "}
                    <a href="https://unsplash.com/photos/FUeb2npsblQ" target="_blank" rel="noopener noreferrer">
                        American Public Power Association
                    </a>
                </div>
            </div>

            <div className="container">
                <section className="page-header">
                    <h1 className="title is-1">Prioritize barriers for removal</h1>
                    <h3 className="subtitle is-3">
                        To prioritize barriers, you will work through the following steps:
                    </h3>
                </section>

                <section className="step" style={{ marginTop: 0 }}>
                    <h4 className="title is-4 flex-container flex-align-center" style={{ marginTop: "1rem" }}>
                        <div className="circle-dark">
                            <div>1</div>
                        </div>
                        <div>Select area of interest.</div>
                    </h4>
                    <p className="is-size-5 has-text-grey">
                        You can select areas using state, county, watershed, and ecoregion boundaries.
                    </p>
                </section>

                <section className="step">
                    <h4 className="title is-4 flex-container flex-align-center" style={{ marginTop: "1rem" }}>
                        <div className="circle-dark">
                            <div>2</div>
                        </div>
                        <div>Filter barriers.</div>
                    </h4>
                    <p className="is-size-5 has-text-grey">
                        You can filter barriers by feasibility, height, and other key characteristics to select those
                        that best meet your needs.
                    </p>
                </section>

                <section className="step">
                    <h4 className="title is-4 flex-container flex-align-center" style={{ marginTop: "1rem" }}>
                        <div className="circle-dark">
                            <div>3</div>
                        </div>
                        <div>Explore priorities on the map.</div>
                    </h4>
                    <p className="is-size-5 has-text-grey">
                        Once you have defined your area of interest and selected the barriers you want, you can explore
                        them on the map.
                    </p>
                </section>

                <section className="step">
                    <h4 className="title is-4 flex-container flex-align-center" style={{ marginTop: "1rem" }}>
                        <div className="circle-dark">
                            <div>4</div>
                        </div>
                        <div>Download prioritized barriers.</div>
                    </h4>
                    <p className="is-size-5 has-text-grey">
                        You can download the inventory for your area of interest and perform offline work.
                    </p>
                </section>

                <section id="ContentPageFooter" style={{ marginTop: "4rem", paddingBottom: "8rem" }}>
                    <h3 className="title is-3">Get started now</h3>
                    <div className="flex-container flex-justify-space-between">
                        <button className="button is-info is-large" type="button" onClick={() => setType("dams")}>
                            <i className="fas fa-search-location" />
                            &nbsp;Prioritize dams
                        </button>
                        <button
                            className="button is-info is-large"
                            type="button"
                            onClick={() => setType("barriers")}
                            style={{ marginLeft: "4rem" }}
                        >
                            <i className="fas fa-search-location" />
                            &nbsp;Prioritize road-related barriers
                        </button>
                    </div>
                </section>
            </div>
        </div>
    )
}

Start.propTypes = {
    setType: PropTypes.func.isRequired
}

export default Start
