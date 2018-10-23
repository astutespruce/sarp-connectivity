import React, { Component } from "react"

class FilterBar extends Component {
    render() {
        const { label, value, valueLabel, range, filtered, onClick } = this.props
        const position = value / range
        const remainder = 1 - position

        return (
            <div className={`filterbar${filtered ? " is-filtered" : ""}`} onClick={onClick}>
                <div className="filterbar-labels">
                    <div className="filterbar-label is-size-7">{label}</div>
                    <div className="filterbar-label-value">{valueLabel}</div>
                </div>
                <div className="filterbar-bars">
                    {position > 0 && <div className="bar" style={{ flexGrow: position }} />}

                    {remainder > 0 && <div className="bar-remainder" style={{ flexGrow: remainder }} />}
                </div>
            </div>
        )
    }
}

FilterBar.defaultProps = {
    filtered: false,
    label: "Category",
    value: 50,
    valueLabel: "50%", // properly formatted version of value for display
    range: 100, // relative range
    onClick: () => {
        console.log("FilterBar: onClick")
    }
}

export default FilterBar
