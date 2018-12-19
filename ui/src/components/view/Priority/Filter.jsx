import React from "react"
import PropTypes from "prop-types"

import { filterConfig } from "../../../filters"

import FilterBars from "../../filterbars/FilterBars"

const Filter = ({ counts, filter, filterValues, onFilterChange, closed, toggleFilterClosed }) => {
    const { title, keys, labelFunction } = filterConfig[filter]

    console.log("count for dim", counts)
    const bars = keys.map((d, idx) => ({
        key: d,
        label: labelFunction(d, idx),
        value: counts.get(d, 0)
    }))
    console.log("bars", bars)

    return (
        <FilterBars
            title={title}
            // range={range}
            bars={bars}
            filterValues={filterValues}
            closed={closed}
            onFilterChange={onFilterChange}
            toggleFilterClosed={toggleFilterClosed}
        />
    )
}

Filter.propTypes = {
    counts: PropTypes.object.isRequired,
    filter: PropTypes.string.isRequired,
    filterValues: PropTypes.arrayOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number])).isRequired,
    closed: PropTypes.bool.isRequired,
    onFilterChange: PropTypes.func.isRequired,
    toggleFilterClosed: PropTypes.func.isRequired
}

export default Filter
