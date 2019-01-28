import React from "react"

import { ScoresPropType } from "../../CustomPropTypes"
import ScoreChart from "./ScoreChart"

const ScoresList = ({ nc, wc, ncwc }) => (
    <div className="priorities-list">
        <ScoreChart label="Network Connectivity" score={nc.score} tier={nc.tier} />
        <ScoreChart label="Watershed Condition" score={wc.score} tier={wc.tier} />
        <ScoreChart label="Network Connectivity & Watershed Condition" score={ncwc.score} tier={ncwc.tier} />
    </div>
)

ScoresList.propTypes = ScoresPropType.isRequired

export default ScoresList
