import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"
import ImmutablePropTypes from "react-immutable-proptypes"

import * as actions from "../../../actions/priority"
import { API_HOST } from "../../../config"
import { apiQueryParams } from "../../../utils/api"
import { formatNumber } from "../../../utils/format"

import StartOverButton from "./StartOverButton"

const Results = ({ type, totalCount, layer, summaryUnits, filters, setMode }) => (
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
            <p className="text-help">Some help text here</p>
            TODO: maybe a slider for tier?
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

Results.propTypes = {
    type: PropTypes.string.isRequired,
    totalCount: PropTypes.number.isRequired,
    layer: PropTypes.string.isRequired,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,

    summaryUnits: ImmutablePropTypes.set.isRequired,

    setMode: PropTypes.func.isRequired
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        type: state.get("type"),
        totalCount: state.get("totalCount"),
        layer: state.get("layer"),
        summaryUnits: state.get("summaryUnits"),
        filters: state.get("filters")
    }
}

export default connect(
    mapStateToProps,
    actions
)(Results)
