import React from "react"
import PropTypes from "prop-types"

const FilterBar = ({ label, value, valueLabel, range, filtered, onClick }) => {
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

FilterBar.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.number.isRequired,
    valueLabel: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,

    filtered: PropTypes.bool,
    range: PropTypes.number // relative range
}

FilterBar.defaultProps = {
    filtered: false,
    range: 100
}

export default FilterBar
