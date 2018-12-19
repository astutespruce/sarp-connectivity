import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { Set } from "immutable"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
import { allFilters } from "../../../filters"

import Filter from "./Filter"

function FiltersList({ filtersLoaded, counts, filters, setFilter, closedFilters, toggleFilterClosed }) {
    console.log("counts", counts.toJS())
    return (
        <div>
            {filtersLoaded ? (
                allFilters.map(f => (
                    <Filter
                        key={f}
                        filter={f}
                        counts={counts.get(f)}
                        filterValues={filters.get(f, Set())}
                        closed={closedFilters.get(f, false)}
                        onFilterChange={v => setFilter(f, v)}
                        toggleFilterClosed={v => toggleFilterClosed(f, v)}
                    />
                ))
            ) : (
                <div>Filters not yet loaded</div>
            )}
        </div>
    )
}

FiltersList.propTypes = {
    filtersLoaded: PropTypes.bool.isRequired,
    counts: ImmutablePropTypes.mapOf(ImmutablePropTypes.mapOf(PropTypes.number)).isRequired,
    filters: ImmutablePropTypes.mapOf(
        ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number]))
    ).isRequired,
    closedFilters: ImmutablePropTypes.mapOf(PropTypes.bool).isRequired,

    setFilter: PropTypes.func.isRequired,
    toggleFilterClosed: PropTypes.func.isRequired
}
const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        filtersLoaded: state.get("filtersLoaded"),
        counts: state.get("dimensionCounts"),
        filters: state.get("filters"),
        closedFilters: state.get("closedFilters")
    }
}

export default connect(
    mapStateToProps,
    actions
)(FiltersList)
