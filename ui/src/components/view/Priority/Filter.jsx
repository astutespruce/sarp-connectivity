import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"

// import { filterConfig } from "../../../filters"

import FilterBars from "../../filterbars/FilterBars"

const Filter = ({ filterConfig, filterValues, counts, onFilterChange, closed, toggleFilterClosed }) => {
    const { title, keys, labelFunction, help = "" } = filterConfig // filterConfig[filter]

    const bars = keys.map((d, idx) => ({
        key: d,
        label: `${labelFunction(d, idx)}`,
        value: counts.get(d, 0)
    }))

    return (
        <FilterBars
            title={title}
            bars={bars}
            help={help}
            filterValues={filterValues}
            closed={closed}
            onFilterChange={onFilterChange}
            toggleFilterClosed={toggleFilterClosed}
        />
    )
}

Filter.propTypes = {
    counts: ImmutablePropTypes.mapOf(PropTypes.number).isRequired,
    filterConfig: PropTypes.shape({}).isRequired,
    filterValues: ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number])).isRequired,
    closed: PropTypes.bool.isRequired,
    // help: PropTypes.string,

    onFilterChange: PropTypes.func.isRequired,
    toggleFilterClosed: PropTypes.func.isRequired
}

export default Filter
