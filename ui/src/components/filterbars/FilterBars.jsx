import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"

import { formatNumber } from "../../utils/format"

import FilterBar from "./FilterBar"
import "./FilterBars.css"

const FilterBars = ({ title, bars, filterValues, closed, onFilterChange, toggleFilterClosed }) => {
    const range = Math.max(...bars.map(b => b.value))

    const handleClick = key => () => {
        if (filterValues.has(key)) {
            onFilterChange(filterValues.delete(key))
        } else {
            onFilterChange(filterValues.add(key))
        }
    }

    const toggleDisplay = () => {
        toggleFilterClosed(!closed)
    }

    const handleReset = () => {
        onFilterChange(filterValues.clear())
    }

    const className = `filterbars${filterValues.size > 0 ? " has-filters" : ""}${closed ? " is-closed" : ""}`

    return (
        <div className={className}>
            <div className="flex-container flex-justify-space-between">
                <h5 className="title is-6 no-margin" onClick={toggleDisplay}>
                    <span className={closed ? "fa fa-caret-right" : "fa fa-caret-down"} />
                    {title}
                </h5>
                <div className="filterbars-reset fa fa-times-circle" onClick={handleReset} title="Clear filter" />
            </div>

            {bars.map(({ key, label, value }, i) => (
                <FilterBar
                    key={i}
                    label={label}
                    value={value}
                    range={range}
                    valueLabel={formatNumber(value, 0)}
                    filtered={filterValues.has(key)}
                    onClick={handleClick(key)}
                />
            ))}
        </div>
    )
}

FilterBars.propTypes = {
    title: PropTypes.string.isRequired,
    bars: PropTypes.arrayOf(
        PropTypes.shape({
            key: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
            label: PropTypes.string.isRequired,
            value: PropTypes.number.isRequired
        })
    ).isRequired,
    filterValues: ImmutablePropTypes.setOf(PropTypes.oneOfType([PropTypes.string, PropTypes.number])).isRequired,
    closed: PropTypes.bool.isRequired,

    onFilterChange: PropTypes.func.isRequired,
    toggleFilterClosed: PropTypes.func.isRequired
}

export default FilterBars
