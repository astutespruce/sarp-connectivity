import React from "react"
import PropTypes from "prop-types"

import { formatNumber } from "../../utils/format"

import { CONDITION, CONSTRUCTION, PURPOSE, RECON } from "../../constants"

const sinuosityLabel = sinuosity => {
    if (sinuosity > 1.5) {
        return "high"
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
    Height,
    Year,
    Construction,
    Purpose,
    Condition,
    River,
    Basin,
    RareSpp,
    Recon,
    // metrics
    GainMiles,
    UpstreamMiles,
    DownstreamMiles,
    Sinuosity,
    Landcover,
    SizeClasses
}) => (
    <div id="BarrierDetails">
        <h6 className="title is-6">Location</h6>
        <ul>
            <li>
                Coordinates: {formatNumber(lon, 3)}
                &deg; W / {formatNumber(lat, 3)}
                &deg; N
            </li>
            <li>
                {River && River !== '"' && River !== "Unknown" ? `${River}, ` : "Unknown river name, "}
                {Basin} Basin
            </li>
        </ul>

        <h6 className="title is-6">Construction information</h6>
        <ul>
            <li>Barrier type: {type === "dam" ? "dam" : "road-related potential barrier"}</li>
            {Year > 0 ? <li>Constructed completed: {Year}</li> : null}
            {Height > 0 ? <li>Height: {Height} feet</li> : null}
            {Construction ? <li>Construction material: {CONSTRUCTION[Construction].toLowerCase()}</li> : null}
            {Purpose ? <li>Purpose: {PURPOSE[Purpose].toLowerCase()}</li> : null}
            {Condition ? <li>Structural condition: {CONDITION[Condition].toLowerCase()}</li> : null}
        </ul>

        <h6 className="title is-6">Functional network information</h6>
        {GainMiles !== null ? (
            <ul>
                <li>
                    <b>{formatNumber(GainMiles, 2)}</b> miles could be gained by removing this barrier
                    <ul>
                        <li>{formatNumber(UpstreamMiles, 2)} miles in the upstream network</li>
                        <li>{formatNumber(DownstreamMiles, 2)} miles in the downstream network</li>
                    </ul>
                </li>
                <li>
                    <b>{SizeClasses}</b> river size {SizeClasses === 1 ? "class" : "classes"} could be gained by
                    removing this barrier
                </li>
                <li>
                    <b>{formatNumber(Landcover, 0)}%</b> of the upstream floodplain is composed of natural landcover
                </li>
                <li>
                    The upstream network has <b>{sinuosityLabel(Sinuosity)}</b> sinuosity
                </li>
            </ul>
        ) : (
            <p className="has-text-grey">No network information available for this barrier.</p>
        )}

        <h6 className="title is-6">Species information</h6>
        <ul>
            {RareSpp > 0 ? (
                <React.Fragment>
                    <li>
                        <b>{RareSpp}</b> threatened and endangered aquatic species have been found in the subwatershed
                        containing this barrier.
                    </li>
                    <li className="has-text-grey is-size-7">
                        Note: species information is very incomplete. These species may or may not be directly impacted
                        by this barrier.
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
            {Recon ? (
                <li>{RECON[Recon]}</li>
            ) : (
                <li className="has-text-grey">No feasibility information is available for this barrier.</li>
            )}
        </ul>
    </div>
)

// TODO: feasibility, metrics

Details.propTypes = {
    lat: PropTypes.number.isRequired,
    lon: PropTypes.number.isRequired,
    type: PropTypes.string.isRequired,
    River: PropTypes.string,
    Basin: PropTypes.string.isRequired,
    Height: PropTypes.number,
    Year: PropTypes.number,
    Construction: PropTypes.number,
    Purpose: PropTypes.number,
    Condition: PropTypes.number,
    RareSpp: PropTypes.number,
    Recon: PropTypes.number,
    GainMiles: PropTypes.number,
    UpstreamMiles: PropTypes.number,
    DownstreamMiles: PropTypes.number,
    Sinuosity: PropTypes.number,
    Landcover: PropTypes.number,
    SizeClasses: PropTypes.number
}

Details.defaultProps = {
    River: "",
    Height: 0,
    Year: 0,
    Construction: 0,
    Purpose: 0,
    Condition: 0,
    RareSpp: 0,
    Recon: 0,
    GainMiles: null,
    UpstreamMiles: null,
    DownstreamMiles: null,
    Sinuosity: null,
    Landcover: null,
    SizeClasses: null
}

export default Details
