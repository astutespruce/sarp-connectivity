// state: summaryunit, metrics expanded.  TODO: put these in global state otherwise we have issues

import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import ScoresList from "./ScoresList"

import { setDetailsUnit } from "../../actions/details"
import { ScoresPropType } from "../../CustomPropTypes"

const Scores = ({ type, tab, scores, setTab }) => {
    const hasCustom = scores.custom && scores.custom.ncwc

    const handleCustomClick = () => setTab("custom")
    const handleStateClick = () => setTab("state")
    const handleRegionclick = () => setTab("se")

    const curScores = scores[tab]

    return (
        <div>
            <h5 className="subtitle is-5 no-margin">Compare to other {type} in the</h5>
            <div className="tabs">
                <ul className="flex-justify-center">
                    {hasCustom ? (
                        <li className={tab === "custom" ? "is-active" : null}>
                            <a onClick={handleCustomClick}>Selected Area</a>
                        </li>
                    ) : null}
                    <li className={tab === "state" ? "is-active" : null}>
                        <a onClick={handleStateClick}>State</a>
                    </li>
                    <li className={tab === "se" ? "is-active" : null}>
                        <a onClick={handleRegionclick}>Southeast</a>
                    </li>
                </ul>
            </div>

            <p className="has-text-grey is-size-7">
                Tiers range from 1 (highest) to 20 (lowest).
                <br />
                <br />
            </p>

            <ScoresList {...curScores} />
        </div>
    )
}

Scores.propTypes = {
    type: PropTypes.string.isRequired,
    tab: PropTypes.string.isRequired,
    scores: PropTypes.shape({
        se: ScoresPropType.isRequired,
        state: ScoresPropType.isRequired,
        custom: ScoresPropType
    }).isRequired,
    setTab: PropTypes.func.isRequired
}

const mapStateToProps = globalState => ({
    type: globalState.get("priority").get("type"),
    tab: globalState.get("details").get("unit")
})

export default connect(
    mapStateToProps,
    { setTab: setDetailsUnit }
)(Scores)
