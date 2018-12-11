import React from "react"

import Section from "./Section"

import { formatNumber } from "../../../utils/format"

import summaryStats from "../../../data/summary_stats.json"

// Photo by American Public Power Association on Unsplash, https://unsplash.com/photos/FUeb2npsblQ
import DamImage from "../../../img/american-public-power-association-430861-unsplash.jpg"

function Inventory() {
    const { dams, connectedmiles } = summaryStats.sarp
    const smallBarriers = 2000000 // FIXME!

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
                        This inventory consists of datasets from local, state, and federal partners, along with input
                        from various partners with on the ground knowledge of specific structures. The information on
                        barriers is not complete and dependent upon the availability and completion of data. Some areas
                        of the region are more complete than others but none should be considered 100% complete.
                    </p>
                </div>
                <div className="column">
                    <div className="info-box">
                        <h5 className="subtitle is-5">At a Glance</h5>
                        <section>
                            <b>14</b> states plus Puerto Rico
                        </section>
                        <section>
                            <b>{formatNumber(dams, 0)}</b> dams
                        </section>
                        <section>
                            <b>{formatNumber(smallBarriers, 0)}</b> road-related barriers
                        </section>
                        <section>
                            <b>{formatNumber(connectedmiles, 1)}</b> miles average connected aquatic network length
                        </section>
                    </div>
                </div>
            </div>
        </Section>
    )
}

export default Inventory
