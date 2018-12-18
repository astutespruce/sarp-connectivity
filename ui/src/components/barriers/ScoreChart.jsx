import React from "react"
import PropTypes from "prop-types"

// All scores are normalized on a 0-1 basis, with 0 being lowest value
const ScoreChart = ({ label, score, lowIcon, highIcon }) => (
    <div className="chart-score">
        <h6 className="title is-6">{label}</h6>
        <div className="flex-container flex-align-center">
            <div>Low</div>
            <div className="domain">
                <div className="domain-line" />
                <div className="marker" style={{ left: `${score}%` }} />
            </div>
            <div>High</div>
        </div>
    </div>
)

ScoreChart.propTypes = {
    label: PropTypes.string.isRequired,
    lowIcon: PropTypes.node,
    highIcon: PropTypes.node,
    score: PropTypes.number.isRequired
}

ScoreChart.defaultProps = {
    lowIcon: null,
    highIcon: null
}

export default ScoreChart
