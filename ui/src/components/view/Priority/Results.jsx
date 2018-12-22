import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"
import ImmutablePropTypes from "react-immutable-proptypes"

import * as actions from "../../../actions/priority"
import { API_HOST } from "../../../config"
import { apiQueryParams } from "../../../utils/api"
import { formatNumber } from "../../../utils/format"

import StartOverButton from "./StartOverButton"
import { SCENARIOS } from "../../map/config"

const Results = ({ type, totalCount, layer, summaryUnits, filters, rankData, setMode }) => {
    const data = rankData.toJS()
    const rankCounts = {}
    Object.keys(SCENARIOS).forEach(scenario => {
        rankCounts[scenario] = data.filter(d => d[`${scenario}_tier`] === 1).length
    })

    return (
        <React.Fragment>
            <div id="SidebarHeader">
                <button className="link link-back" type="button" onClick={() => setMode("filter")}>
                    <span className="fa fa-reply" />
                    &nbsp; modify filters
                </button>
                <h4 className="title is-4 no-margin">Explore results</h4>
                <div className="has-text-gray flex-container flex-justify-space-between">
                    <div>
                        {formatNumber(totalCount, 0)} prioritized {type}
                    </div>
                </div>
            </div>
            <div id="SidebarContent">
                <h6 className="title is-6">Top-ranked {type}:</h6>
                <ul>
                    {Object.entries(SCENARIOS).map(([key, name]) => (
                        <li key={key}>
                            {name}: {rankCounts[key]}
                        </li>
                    ))}
                </ul>
                <p className="text-help">
                    <br />
                    <br />
                    TODO: totally need to finish this section.
                    <br />
                    <br />
                    for now, click on points on the map or download
                </p>
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
    totalCount: PropTypes.number.isRequired,
    layer: PropTypes.string.isRequired,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,

    summaryUnits: ImmutablePropTypes.set.isRequired,
    rankData: ImmutablePropTypes.listOf(ImmutablePropTypes.map).isRequired,

    setMode: PropTypes.func.isRequired
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        type: state.get("type"),
        totalCount: state.get("totalCount"),
        layer: state.get("layer"),
        summaryUnits: state.get("summaryUnits"),
        filters: state.get("filters"),
        rankData: state.get("rankData")
    }
}

export default connect(
    mapStateToProps,
    actions
)(Results)
