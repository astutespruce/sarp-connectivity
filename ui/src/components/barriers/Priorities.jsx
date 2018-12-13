// state: summaryunit, metrics expanded.  TODO: put these in global state otherwise we have issues

import React from "react"
import PropTypes from "prop-types"

import PrioritiesList from "./PrioritiesList"

import { BarrierPrioritiesPropType, MetricsPropType } from "../../CustomPropTypes"

const Priorities = ({ tab, metrics, metricScores, priorities, setTab }) => {
    const hasCustom = priorities.custom && priorities.custom.nc

    const handleCustomClick = () => setTab("custom")
    const handleStateClick = () => setTab("state")
    const handleRegionclick = () => setTab("se")

    const curPriorities = priorities[tab]
    console.log(curPriorities)

    return (
        <div>
            <h5 className="subtitle is-5 no-margin">Compare to other dams in the</h5>
            <div className="tabs">
                <ul className="flex-justify-center">
                    {hasCustom && (
                        <li className={tab === "custom" ? "is-active" : null}>
                            <a onClick={handleCustomClick}>Selected Area</a>
                        </li>
                    )}
                    <li className={tab === "state" ? "is-active" : null}>
                        <a onClick={handleStateClick}>State</a>
                    </li>
                    <li className={tab === "se" ? "is-active" : null}>
                        <a onClick={handleRegionclick}>Southeast</a>
                    </li>
                </ul>
            </div>

            <PrioritiesList {...curPriorities} />
        </div>
    )
}

Priorities.propTypes = {
    tab: PropTypes.string,
    metrics: MetricsPropType.isRequired,
    priorities: BarrierPrioritiesPropType.isRequired,
    setTab: PropTypes.func
}

Priorities.defaultProps = {
    tab: "state",
    setTab: tab => {
        console.log(`Set Tab: ${tab}`)
    }
}

export default Priorities
