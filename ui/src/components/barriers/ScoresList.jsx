import React from "react"

import { ScoresPropType } from "../../CustomPropTypes"
import ScoreChart from "./ScoreChart"

const ScoresList = ({ NC, WC, NCWC }) => (
    <div className="priorities-list">
        <ScoreChart label="Network Connectivity" score={NC} />
        <ScoreChart label="Watershed Condition" score={WC} />
        <ScoreChart label="Network Connectivity & Watershed Condition" score={NCWC} />
    </div>
)

ScoresList.propTypes = ScoresPropType.isRequired

export default ScoresList
