import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { Set } from "immutable"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
import { allFilters } from "../../../filters"

import Filter from "./Filter"

function FiltersList({ type, counts, filters, setFilter, closedFilters, toggleFilterClosed, setMode }) {
    console.log("counts", counts.toJS())
    return (
        <React.Fragment>
            <div id="SidebarHeader">
                <button className="link link-back" type="button" onClick={() => setMode("select")}>
                    <span className="fa fa-reply" />
                    &nbsp; modify area of interest
                </button>
                <h4 className="title is-4">Filter {type}</h4>
            </div>
            <div id="SidebarContent">
                {allFilters.map(f => (
                    <Filter
                        key={f}
                        filter={f}
                        counts={counts.get(f)}
                        filterValues={filters.get(f, Set())}
                        closed={closedFilters.get(f, false)}
                        onFilterChange={v => setFilter(f, v)}
                        toggleFilterClosed={v => toggleFilterClosed(f, v)}
                    />
                ))}
            </div>
        </React.Fragment>
    )
}

FiltersList.propTypes = {
    type: PropTypes.string.isRequired,
    counts: ImmutablePropTypes.mapOf(ImmutablePropTypes.mapOf(PropTypes.number)).isRequired,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,
    closedFilters: ImmutablePropTypes.mapOf(PropTypes.bool).isRequired,

    setFilter: PropTypes.func.isRequired,
    toggleFilterClosed: PropTypes.func.isRequired,
    setMode: PropTypes.func.isRequired
}
const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        type: state.get("type"),
        counts: state.get("dimensionCounts"),
        filters: state.get("filters"),
        closedFilters: state.get("closedFilters")
    }
}

export default connect(
    mapStateToProps,
    actions
)(FiltersList)
