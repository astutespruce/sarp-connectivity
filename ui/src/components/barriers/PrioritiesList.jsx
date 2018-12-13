import React from "react"
import PropTypes from "prop-types"

import { PrioritiesPropType } from "../../CustomPropTypes"
import ScoreChart from "./ScoreChart"

const sortedPriorities = ["nc", "wc", "ncwc"]
const priorityLabels = {
    nc: "Network Connectivity",
    wc: "Watershed Condition",
    ncwc: "Network Connectivity and Watershed Condition"
}

const PrioritiesList = ({ nc, wc, ncwc }) => (
    <div className="priorities-list">
        <ScoreChart label="Network Connectivity" score={nc} />
        <ScoreChart label="Watershed Condition" score={wc} />
        <ScoreChart label="Network Connectivity & Watershed Condition" score={ncwc} />
    </div>
)

PrioritiesList.propTypes = {
    // priorities: PrioritiesPropType.isRequired,
    nc: PropTypes.number.isRequired,
    wc: PropTypes.number.isRequired,
    ncwc: PropTypes.number.isRequired
}

export default PrioritiesList
