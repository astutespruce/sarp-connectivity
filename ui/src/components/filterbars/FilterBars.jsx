import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"

import FilterBar from "./FilterBar"

import "./FilterBars.css"

const FilterBars = ({ title, bars, filterValues, closed, formatter, onFilterChange, toggleFilterClosed }) => {
    const handleClick = key => () => {
        console.log("handle click", key, filterValues.add(key).toJS())
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

    console.log("filterValues", filterValues.toJS())

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
                    valueLabel={formatter(value)}
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
    toggleFilterClosed: PropTypes.func.isRequired,

    formatter: PropTypes.func
}

FilterBars.defaultProps = {
    formatter(v) {
        return `${v}`
    }
}

export default FilterBars

// import React, { Component } from "react"
// import FilterBar from "./FilterBar"
// import "./FilterBars.css"

// class FilterBars extends Component {
//     handleClick = (key, filterValues) => {
//         filterValues = filterValues === null ? new Set() : new Set(filterValues)

//         if (filterValues === null || filterValues.size === 0) {
//             this.props.onFilterChange(new Set([key]))
//         }

//         filterValues = new Set(filterValues) // deep copy filter values

//         // toggle filter key presence in the set
//         if (filterValues.has(key)) {
//             filterValues.delete(key)
//         } else {
//             filterValues.add(key)
//         }
//         return this.props.onFilterChange(filterValues)
//     }

//     toggleDisplay = () => {
//         this.props.toggleFilterClosed(!this.props.closed)
//     }

//     handleReset = () => {
//         this.props.onFilterChange(null)
//     }

//     renderBars = (bar, index) => {
//         const { formatter, range, filterValues } = this.props
//         const { key, label, value } = bar

//         const isFiltered = !!(filterValues && filterValues.has(key))

//         return (
//             <FilterBar
//                 key={index}
//                 label={label}
//                 value={value}
//                 range={range}
//                 valueLabel={formatter(value)}
//                 filtered={isFiltered}
//                 onClick={() => this.handleClick(key, filterValues)}
//             />
//         )
//     }

//     render() {
//         const { bars, title, filterValues, closed } = this.props

//         const className = `filterbars${filterValues && filterValues.size > 0 ? " has-filters" : ""}${
//             closed ? " is-closed" : ""
//         }`

//         return (
//             <div className={className}>
//                 <div className="flex-row flex-justify-space-between">
//                     <h5 className="title is-6 no-margin" onClick={this.toggleDisplay}>
//                         <span className={closed ? "fa fa-caret-right" : "fa fa-caret-down"} />
//                         {title}
//                     </h5>
//                     <div
//                         className="filterbars-reset fa fa-times-circle"
//                         onClick={this.handleReset}
//                         title="Clear filter"
//                     />
//                 </div>

//                 {bars.map(this.renderBars)}
//             </div>
//         )
//     }
// }

// FilterBars.defaultProps = {
//     title: "Title",
//     bars: [], // [{key: 'foo', value: 10, label: 'Foo'}...]
//     range: 100, // relative range
//     formatter(v) {
//         return `${v}`
//     },
//     closed: false,
//     filterValues: null, // Set([filterValue,...])
//     toggleFilterClosed: closed => {
//         console.log("Setting filterbars closed?", closed)
//     },
//     onFilterChange: filters => {
//         console.log("FilterBars: onFilterChange, current filters:", filters)
//     }
// }

// export default FilterBars
