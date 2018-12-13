// state: summaryunit, metrics expanded.  TODO: put these in global state otherwise we have issues

import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import PrioritiesList from "./PrioritiesList"

import { BarrierPrioritiesPropType, MetricsPropType } from "../../CustomPropTypes"

import { setDetailsUnit } from "../../actions/details"

const Priorities = ({ tab, metricScores, priorities, setTab }) => {
    const hasCustom = priorities.custom && priorities.custom.nc

    const handleCustomClick = () => setTab("custom")
    const handleStateClick = () => setTab("state")
    const handleRegionclick = () => setTab("se")

    const curPriorities = priorities[tab]

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
    tab: PropTypes.string.isRequired,
    metricScores: MetricsPropType.isRequired,
    priorities: BarrierPrioritiesPropType.isRequired,
    setTab: PropTypes.func
}

Priorities.defaultProps = {
    setTab: tab => {
        console.log(`Set Tab: ${tab}`)
    }
}

const mapStateToProps = globalState => {
    const state = globalState.get("details")
    return {
        tab: state.get("unit")
    }
}

// const mapDispatchToProps = (dispatch) => {
//     return {
//         setTab:
//     }
// }

export default connect(
    mapStateToProps,
    { setTab: setDetailsUnit }
)(Priorities)
