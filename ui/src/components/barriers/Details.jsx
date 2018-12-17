import React from "react"
import PropTypes from "prop-types"

import { formatNumber } from "../../utils/format"

import { MetricsPropType } from "../../CustomPropTypes"

const sinuosityLabel = sinuosity => {
    if (sinuosity > 1.5) {
        return "higher"
    }
    if (sinuosity >= 1.2) {
        return "moderate"
    }
    return "low"
}

const Details = ({
    lat,
    lon,
    type,
    height,
    year,
    material,
    purpose,
    condition,
    river,
    basin,
    metrics,
    numSpp,
    feasibility
}) => {
    const { length, upstreamMiles, downstreamMiles, sinuosity, sizeclasses, landcover } = metrics
    const hasMetrics = metrics !== null

    return (
        <div id="BarrierDetails">
            <h6 className="title is-6">Location</h6>
            <ul>
                <li>
                    Coordinates: {formatNumber(lon, 3)}
                    &deg; W / {formatNumber(lat, 3)}
                    &deg; N
                </li>
                <li>
                    {river && `${river}, `}
                    {basin} Basin
                </li>
            </ul>

            <h6 className="title is-6">Construction information</h6>
            <ul>
                <li>Barrier type: {type === "smallBarrier" ? "road-related potential barrier" : "dam"}</li>
                {year > 0 && <li>Constructed in {year}</li>}
                {height > 0 && <li>Height: {height} feet</li>}
                {material && <li>Construction material: {material.toLowerCase()}</li>}
                {purpose && <li>Purpose: {purpose.toLowerCase()}</li>}
                {condition && <li>Structural condition: {condition.toLowerCase()}</li>}
            </ul>

            <h6 className="title is-6">Functional network information</h6>
            {hasMetrics ? (
                <ul>
                    <li>
                        <b>{formatNumber(length)}</b> miles could be gained by removing this barrier
                        <ul>
                            <li>{formatNumber(upstreamMiles)} miles in the upstream network</li>
                            <li>{formatNumber(downstreamMiles)} miles in the downstream network</li>
                        </ul>
                    </li>
                    <li>
                        <b>{sizeclasses}</b> river size {sizeclasses === 1 ? "class" : "classes"} could be gained by
                        removing this barrier
                    </li>
                    <li>
                        <b>{formatNumber(landcover, 0)}%</b> of the upstream floodplain is composed of natural landcover
                    </li>
                    <li>
                        The upstream network has <b>{sinuosityLabel(sinuosity)}</b> sinuosity
                    </li>
                </ul>
            ) : (
                <p className="has-text-grey">No network information available for this barrier.</p>
            )}

            <h6 className="title is-6">Species information</h6>
            <ul>
                {numSpp > 0 ? (
                    <React.Fragment>
                        <li>
                            <b>{numSpp}</b> threatened and endangered aquatic species have been found in the
                            subwatershed containing this barrier.
                        </li>
                        <li className="has-text-grey is-size-7">
                            Note: species information is very incomplete. These species may or may not be directly
                            impacted by this barrier.
                        </li>
                    </React.Fragment>
                ) : (
                    <li className="has-text-grey">
                        No threatened and endangered aquatic species occurrence information is available for this
                        subwatershed.
                    </li>
                )}
            </ul>

            <h6 className="title is-6">Feasibility of removal</h6>
            <ul>
                {feasibility ? (
                    <li>{feasibility}</li>
                ) : (
                    <li className="has-text-grey">No feasibility information is available for this barrier.</li>
                )}
            </ul>
        </div>
    )
}

// TODO: feasibility, metrics

Details.propTypes = {
    lat: PropTypes.number.isRequired,
    lon: PropTypes.number.isRequired,
    type: PropTypes.string.isRequired,
    river: PropTypes.string,
    basin: PropTypes.string.isRequired,
    height: PropTypes.number,
    year: PropTypes.number,
    material: PropTypes.string,
    purpose: PropTypes.string,
    condition: PropTypes.string,
    metrics: MetricsPropType,
    numSpp: PropTypes.number,
    feasibility: PropTypes.string
}

Details.defaultProps = {
    river: "",
    height: 0,
    year: 0,
    material: "",
    purpose: "",
    condition: "",
    metrics: null,
    numSpp: 0,
    feasibility: ""
}

export default Details
