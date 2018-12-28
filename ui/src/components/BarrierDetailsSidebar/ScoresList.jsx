import React from "react"

import { ScoresPropType } from "../../CustomPropTypes"
import ScoreChart from "./ScoreChart"

const ScoresList = ({ nc, wc, ncwc }) => (
    <div className="priorities-list">
        <ScoreChart label="Network Connectivity" score={nc} />
        <ScoreChart label="Watershed Condition" score={wc} />
        <ScoreChart label="Network Connectivity & Watershed Condition" score={ncwc} />
    </div>
)

ScoresList.propTypes = ScoresPropType.isRequired

export default ScoresList
