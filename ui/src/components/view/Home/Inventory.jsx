import React from "react"

import Section from "../../Section"

import { formatNumber } from "../../../utils/format"

import summaryStats from "../../../data/summary_stats.json"

// Photo by American Public Power Association on Unsplash, https://unsplash.com/photos/FUeb2npsblQ
import DamImage from "../../../img/american-public-power-association-430861-unsplash.jpg"

function Inventory() {
    const { dams, barriers, miles } = summaryStats.southeast

    return (
        <Section image={DamImage} dark title="The Southeast Aquatic Barrier Inventory">
            <div className="columns">
                <div className="column is-two-thirds">
                    <p>
                        This inventory is a growing and living database of dams and road / stream crossings compiled by
                        the Southeast Aquatic Resources Partnership with the generous support from many partners and
                        funders. Information about network connectivity, landscape condition, and presence of threatened
                        and endangered aquatic organisms are added to this inventory to help you investigate barriers at
                        any scale for your desired purposes.
                        <br />
                        <br />
                        This inventory consists of datasets from local, state, and federal partners. It is supplemented
                        with input from partners with on the ground knowledge of specific structures. The information on
                        barriers is not complete or comprehensive across the region, and depends on the availability and
                        completeness of existing data. Some areas of the region are more complete than others but none
                        should be considered 100% complete.
                        <br />
                        <br />
                    </p>
                    <h4 className="title is-5" style={{ marginBottom: 0 }}>
                        Get involved!
                    </h4>
                    <p>
                        If you are able to help improve the inventory by sharing data or assisting with field
                        reconnaissance, please <a href="mailto:kat@southeastaquatics.net">contact us</a>.
                    </p>
                </div>
                <div className="column">
                    <div className="info-box">
                        <h5 className="subtitle is-4 text-align-center">At a Glance</h5>
                        <section>
                            <b className="is-size-4 has-text-grey-dark">14</b> states and Puerto Rico
                        </section>
                        <section>
                            <b className="is-size-4 has-text-grey-dark">{formatNumber(dams, 0)}</b> dams
                        </section>
                        <section>
                            <b className="is-size-4 has-text-grey-dark">{formatNumber(barriers, 0)}</b> road-related
                            barriers assessed for impact to aquatic organisms
                        </section>
                        <section>
                            <b className="is-size-4 has-text-grey-dark">{formatNumber(miles, 1)}</b> miles of connected
                            aquatic network length, on average
                        </section>
                    </div>
                </div>
            </div>
        </Section>
    )
}

export default Inventory
