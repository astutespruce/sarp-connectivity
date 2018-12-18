// state: summaryunit, metrics expanded.  TODO: put these in global state otherwise we have issues

import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import ScoresList from "./ScoresList"

import { setDetailsUnit } from "../../actions/details"
import { ScoresPropType } from "../../CustomPropTypes"

const Scores = ({ tab, scores, setTab }) => {
    const hasCustom = scores.custom && scores.custom.GainMiles

    const handleCustomClick = () => setTab("custom")
    const handleStateClick = () => setTab("State")
    const handleRegionclick = () => setTab("SE")

    const curScores = scores[tab]

    console.log(curScores)

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
                    <li className={tab === "State" ? "is-active" : null}>
                        <a onClick={handleStateClick}>State</a>
                    </li>
                    <li className={tab === "SE" ? "is-active" : null}>
                        <a onClick={handleRegionclick}>Southeast</a>
                    </li>
                </ul>
            </div>

            <ScoresList {...curScores} />
        </div>
    )
}

Scores.propTypes = {
    tab: PropTypes.string.isRequired,
    scores: PropTypes.shape({
        SE: ScoresPropType.isRequired,
        State: ScoresPropType.isRequired,
        custom: ScoresPropType
    }).isRequired,
    setTab: PropTypes.func
}

Scores.defaultProps = {
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

export default connect(
    mapStateToProps,
    { setTab: setDetailsUnit }
)(Scores)
