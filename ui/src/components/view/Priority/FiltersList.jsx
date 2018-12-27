import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { Set } from "immutable"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
import { allFilters, filterConfig } from "../../../filters"
import { formatNumber } from "../../../utils/format"

import StartOverButton from "./StartOverButton"
import SubmitButton from "./SubmitButton"
import Filter from "./Filter"

function FiltersList({
    layer,
    type,
    counts,
    totalCount,
    filters,
    summaryUnits,
    setFilter,
    resetFilters,
    closedFilters,
    toggleFilterClosed,
    setMode,
    fetchRanks
}) {
    const handleResetFilters = () => {
        resetFilters()
    }

    const hasFilters = Object.values(filters.toJS()).reduce((out, v) => out + v.length, 0) > 0

    return (
        <React.Fragment>
            <div id="SidebarHeader">
                <button className="link link-back" type="button" onClick={() => setMode("select")}>
                    <span className="fa fa-reply" />
                    &nbsp; modify area of interest
                </button>
                <h4 className="title is-4 no-margin">Filter {type}</h4>
                <div className="has-text-grey flex-container flex-justify-space-between">
                    <div>{formatNumber(totalCount, 0)} selected</div>
                    {hasFilters ? (
                        <button
                            className="link"
                            type="button"
                            onClick={handleResetFilters}
                            style={{ color: "#ee7d14" }}
                        >
                            <i className="fas fa-times-circle" />
                            &nbsp; reset filters
                        </button>
                    ) : null}
                </div>
            </div>
            <div id="SidebarContent">
                <p className="text-help">
                    [OPTIONAL] Use the filters below to select the {type} that meet your needs. Click on a bar to select{" "}
                    {type} with that value. Click on the bar again to unselect. You can combine multiple values across
                    multiple filters to select the {type} that match ANY of those values within a filter and also have
                    the values selected across ALL filters.
                </p>
                <div style={{ marginTop: "1rem" }}>
                    {allFilters.map(f => (
                        <Filter
                            key={f}
                            filter={f}
                            counts={counts.get(f)}
                            filterValues={filters.get(f, Set())}
                            closed={closedFilters.get(f, false)}
                            help={filterConfig[f].help}
                            onFilterChange={v => setFilter(f, v)}
                            toggleFilterClosed={v => toggleFilterClosed(f, v)}
                        />
                    ))}
                </div>
            </div>

            <div id="SidebarFooter">
                <div className="flex-container flex-justify-center flex-align-center">
                    <StartOverButton />

                    <SubmitButton
                        disabled={totalCount === 0}
                        onClick={() => fetchRanks(type, layer, summaryUnits.toJS(), filters.toJS())}
                        icon="search-location"
                        label={`Prioritize ${type}`}
                    />
                </div>
            </div>
        </React.Fragment>
    )
}

FiltersList.propTypes = {
    type: PropTypes.string.isRequired,
    layer: PropTypes.string.isRequired,
    counts: ImmutablePropTypes.mapOf(ImmutablePropTypes.mapOf(PropTypes.number)).isRequired,
    totalCount: PropTypes.number.isRequired,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,
    closedFilters: ImmutablePropTypes.mapOf(PropTypes.bool).isRequired,

    summaryUnits: ImmutablePropTypes.set.isRequired,
    setFilter: PropTypes.func.isRequired,
    resetFilters: PropTypes.func.isRequired,
    toggleFilterClosed: PropTypes.func.isRequired,
    setMode: PropTypes.func.isRequired,
    fetchRanks: PropTypes.func.isRequired
}
const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        type: state.get("type"),
        layer: state.get("layer"),
        counts: state.get("dimensionCounts"),
        totalCount: state.get("totalCount"),
        filters: state.get("filters"),
        closedFilters: state.get("closedFilters"),
        summaryUnits: state.get("summaryUnits")
    }
}

export default connect(
    mapStateToProps,
    actions
)(FiltersList)
