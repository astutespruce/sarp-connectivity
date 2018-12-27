/* eslint-disable react/no-array-index-key */
import React from "react"
import PropTypes from "prop-types"

import { formatNumber } from "../../../utils/format"

const Histogram = ({ counts, threshold }) => {
    const margin = "0.25em"
    const max = Math.max(...counts)

    const labelWidth = max.toString().length * 0.75

    return (
        <div className="histogram">
            <div className="histogram-bars flex-grow">
                {counts.map((count, i) => (
                    <div key={`${i}-${count}`} className="flex-container flex-align-center">
                        <div className="is-size-7 histogram-label">Tier {i + 1}</div>
                        <div className="bar-container flex-container flex-align-center flex-grow">
                            <div
                                className={`bar ${i + 1 <= threshold ? "top" : ""}`}
                                style={{
                                    width: `calc(${(100 * count) / max}% - ${labelWidth}em - ${margin})`,
                                    marginRight: margin
                                }}
                            />
                            <div className="is-size-7 has-text-grey">{formatNumber(count, 0)}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

Histogram.propTypes = {
    counts: PropTypes.arrayOf(PropTypes.number).isRequired,
    threshold: PropTypes.number.isRequired
}

export default Histogram
