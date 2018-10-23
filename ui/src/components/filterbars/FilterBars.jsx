import React, { Component } from "react"
import FilterBar from "./FilterBar"
import "./FilterBars.css"

class FilterBars extends Component {
    handleClick = (key, filterValues) => {
        filterValues = filterValues === null ? new Set() : new Set(filterValues)

        if (filterValues === null || filterValues.size === 0) {
            this.props.onFilterChange(new Set([key]))
        }

        filterValues = new Set(filterValues) // deep copy filter values

        // toggle filter key presence in the set
        if (filterValues.has(key)) {
            filterValues.delete(key)
        } else {
            filterValues.add(key)
        }
        return this.props.onFilterChange(filterValues)
    }

    toggleDisplay = () => {
        this.props.toggleFilterClosed(!this.props.closed)
    }

    handleReset = () => {
        this.props.onFilterChange(null)
    }

    renderBars = (bar, index) => {
        const { formatter, range, filterValues } = this.props
        const { key, label, value } = bar

        const isFiltered = !!(filterValues && filterValues.has(key))

        return (
            <FilterBar
                key={index}
                label={label}
                value={value}
                range={range}
                valueLabel={formatter(value)}
                filtered={isFiltered}
                onClick={() => this.handleClick(key, filterValues)}
            />
        )
    }

    render() {
        const { bars, title, filterValues, closed } = this.props

        const className = `filterbars${filterValues && filterValues.size > 0 ? " has-filters" : ""}${
            closed ? " is-closed" : ""
        }`

        return (
            <div className={className}>
                <div className="flex-row flex-justify-space-between">
                    <h5 className="title is-6 no-margin" onClick={this.toggleDisplay}>
                        <span className={closed ? "fa fa-caret-right" : "fa fa-caret-down"} />
                        {title}
                    </h5>
                    <div
                        className="filterbars-reset fa fa-times-circle"
                        onClick={this.handleReset}
                        title="Clear filter"
                    />
                </div>

                {bars.map(this.renderBars)}
            </div>
        )
    }
}

FilterBars.defaultProps = {
    title: "Title",
    bars: [], // [{key: 'foo', value: 10, label: 'Foo'}...]
    range: 100, // relative range
    formatter(v) {
        return `${v}`
    },
    closed: false,
    filterValues: null, // Set([filterValue,...])
    toggleFilterClosed: closed => {
        console.log("Setting filterbars closed?", closed)
    },
    onFilterChange: filters => {
        console.log("FilterBars: onFilterChange, current filters:", filters)
    }
}

export default FilterBars
