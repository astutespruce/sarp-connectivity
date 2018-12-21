import React from "react"
import PropTypes from "prop-types"

const Legend = ({ title, entries }) => (
    <div id="Legend">
        <h5 className="title is-6">{title}</h5>
        {entries.map(({ label, color, borderColor, size }) => (
            <div key={label} className="legend-row flex-container flex-align-center">
                <div
                    className="legend-patch-point"
                    style={{ backgroundColor: color, width: size, height: size, borderRadius: size, borderColor: borderColor || color }}
                />
                <div className="legend-label">{label}</div>
            </div>
        ))}
    </div>
)

Legend.propTypes = {
    title: PropTypes.string,
    entries: PropTypes.arrayOf(
        PropTypes.shape({
            label: PropTypes.string.isRequired,
            color: PropTypes.string.isRequired,
            size: PropTypes.number.isRequired,
            borderColor: PropTypes.string.isRequired
        })
    )
}

Legend.defaultProps = {
    title: "Legend",
    entries: []
}

export default Legend
