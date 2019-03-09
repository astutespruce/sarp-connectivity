import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"
import ImmutablePropTypes from "react-immutable-proptypes"
import debounce from "lodash.debounce"

import * as actions from "../../../actions/priority"
import { API_HOST } from "../../../config"
import { SCENARIOS } from "../../../constants"
import { apiQueryParams } from "../../../utils/api"
import { formatNumber } from "../../../utils/format"

import Histogram from "./Histogram"

import StartOverButton from "./StartOverButton"

const Results = ({
    type,
    scenario,
    totalCount,
    layer,
    summaryUnits,
    filters,
    rankData,
    setMode,
    tierThreshold,
    setTierThreshold,
    logDownload
}) => {
    const scenarioLabel =
        scenario === "ncwc"
            ? "combined network connectivity and watershed condition"
            : SCENARIOS[scenario].toLowerCase()

    const tierCounts = {}
    rankData.toJS().forEach(d => {
        const tier = d[`${scenario}_tier`]
        if (!tierCounts[tier]) {
            tierCounts[tier] = 0
        }
        tierCounts[tier] += 1
    })

    const tiers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    const counts = tiers.map(i => tierCounts[i] || 0)

    const handleThresholdChange = ({ target: { value } }) => {
        debounce(() => setTierThreshold(21 - value), 50)()
    }

    return (
        <React.Fragment>
            <div id="SidebarHeader">
                <button className="link link-back" type="button" onClick={() => setMode("filter")}>
                    <span className="fa fa-reply" />
                    &nbsp; modify filters
                </button>
                <h4 className="title is-4 no-margin">Explore results</h4>
                <div className="has-text-grey flex-container flex-justify-space-between">
                    <div>
                        {formatNumber(totalCount, 0)} prioritized {type}
                    </div>
                </div>
            </div>
            <div id="SidebarContent">
                <p className="has-text-grey">
                    {type.slice(0, 1).toUpperCase() + type.slice(1)} are binned into tiers based on where they fall
                    within the value range of the <b>{scenarioLabel}</b> score. Tier 1 includes {type} that fall within
                    the top 5% of values for this score, and tier 20 includes {type} that fall within the lowest 5% of
                    values for this score.
                    <br />
                    <br />
                </p>

                <div style={{ margin: "2rem 0" }}>
                    <h6 className="title is-6 no-margin">Choose top-ranked dams for display on map</h6>

                    <div className="flex-container" style={{ margin: "1rem" }}>
                        <div className="is-size-7">Lowest tier</div>
                        <input
                            type="range"
                            min="1"
                            max="20"
                            step="1"
                            className="flex-grow"
                            value={21 - tierThreshold}
                            onChange={handleThresholdChange}
                        />
                        <div className="is-size-7">Highest tier</div>
                    </div>
                    <p className="has-text-grey">
                        Use this slider to control the number of tiers visible on the map. Based on the number of {type}{" "}
                        visible for your area, you may be able to identify {type} that are more feasible in the top
                        several tiers than in the top-most tier.
                    </p>
                </div>

                <h6 className="title is-6 no-margin">Number of dams by tier</h6>

                <Histogram counts={counts} threshold={tierThreshold} />
            </div>

            <div id="SidebarFooter">
                <div className="flex-container flex-justify-center flex-align-center">
                    <StartOverButton />

                    <a
                        href={`${API_HOST}/api/v1/${type}/csv/${layer}?${apiQueryParams(
                            summaryUnits.toJS(),
                            filters.toJS()
                        )}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="button is-info is-medium"
                        onClick={() => logDownload()}
                    >
                        <i className="fa fa-download" style={{ marginRight: "0.25em" }} />
                        Download {type}
                    </a>
                </div>
            </div>
        </React.Fragment>
    )
}

Results.propTypes = {
    type: PropTypes.string.isRequired,
    scenario: PropTypes.string.isRequired,
    totalCount: PropTypes.number.isRequired,
    layer: PropTypes.string.isRequired,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,

    summaryUnits: ImmutablePropTypes.set.isRequired,
    rankData: ImmutablePropTypes.listOf(ImmutablePropTypes.map).isRequired,

    tierThreshold: PropTypes.number.isRequired,

    setMode: PropTypes.func.isRequired,
    setTierThreshold: PropTypes.func.isRequired,
    logDownload: PropTypes.func.isRequired
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")
    const crossfilter = globalState.get("crossfilter")

    return {
        type: state.get("type"),
        scenario: state.get("scenario"),
        layer: state.get("layer"),
        summaryUnits: state.get("summaryUnits"),
        rankData: state.get("rankData"),
        tierThreshold: state.get("tierThreshold"),

        filters: crossfilter.get("filters"),
        totalCount: crossfilter.get("filteredCount")
    }
}

export default connect(
    mapStateToProps,
    actions
)(Results)
