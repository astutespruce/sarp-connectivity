import React from "react"
import PropTypes from "prop-types"

const Legend = ({ colors, labels }) => {
    // flip the order since we are displaying from top to bottom
    colors.reverse()
    labels.reverse()
    return (
        <div id="Legend">
            <h5 className="is-size-6">Legend</h5>
            <div className="flex-container">
                <div>
                    {colors.map(backgroundColor => (
                        <div key={backgroundColor} className="legend-patch" style={{ backgroundColor }} />
                    ))}
                </div>
                <div className="flex-container-column flex-justify-space-between">
                    {labels.map(label => (
                        <div key={label} className="legend-label is-size-7">{label}</div>
                    ))}
                </div>
            </div>
        </div>
    )
}

Legend.propTypes = {
    colors: PropTypes.arrayOf(PropTypes.string).isRequired,
    labels: PropTypes.arrayOf(PropTypes.string).isRequired
}

Legend.defaultProps = {}

export default Legend
