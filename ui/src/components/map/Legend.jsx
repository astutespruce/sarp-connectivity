import React from "react"
import PropTypes from "prop-types"

const Legend = ({ colors, labels, title, footnote }) => (
    <div id="Legend">
        <h5 className="is-size-6">{title}</h5>
        <div className="flex-container">
            <div>
                {colors.map(backgroundColor => (
                    <div key={backgroundColor} className="legend-patch" style={{ backgroundColor }} />
                ))}
            </div>
            <div className="flex-container-column flex-justify-space-between">
                {labels.map(label => (
                    <div key={label} className="legend-label is-size-7">
                        {label}
                    </div>
                ))}
            </div>
        </div>
        {footnote && (
            <div id="LegendFootnote" className="is-size-7 has-text-grey">
                {footnote}
            </div>
        )}
    </div>
)

Legend.propTypes = {
    colors: PropTypes.arrayOf(PropTypes.string).isRequired,
    labels: PropTypes.arrayOf(PropTypes.string).isRequired,
    title: PropTypes.string,
    footnote: PropTypes.string
}

Legend.defaultProps = {
    title: "Legend",
    footnote: null
}

export default Legend
