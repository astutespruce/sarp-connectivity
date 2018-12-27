import React from "react"
import PropTypes from "prop-types"

import { formatNumber } from "../../utils/format"

import { SINUOSITY } from "../../constants"

const BarrierDetails = ({
    lat,
    lon,
    hasnetwork,
    stream,
    basin,
    road,
    roadtype,
    crossingtype,
    condition,
    rarespp,
    potentialproject,
    // metrics
    gainmiles,
    upstreammiles,
    downstreammiles,
    sinuosity,
    landcover,
    sizeclasses
}) => {
    const isCrossing = roadtype === ""

    return (
        <div id="BarrierDetails">
            <h6 className="title is-6">Location</h6>
            <ul>
                <li>
                    Coordinates: {formatNumber(lon, 3)}
                    &deg; W / {formatNumber(lat, 3)}
                    &deg; N
                </li>
                {stream && stream !== "null" ? (
                    <li>
                        Stream or river: {stream}
                        {basin ? `, ${basin} Basin` : null}
                    </li>
                ) : null}
                {road ? <li>Road: {road}</li> : null}
            </ul>

            <h6 className="title is-6">Barrier information</h6>
            <ul>
                <li>Barrier type: {isCrossing ? "road / stream crossing" : "road-related potential barrier"}</li>
                {roadtype ? <li>Road type: {roadtype}</li> : null}
                {crossingtype ? <li>Crossing type: {crossingtype}</li> : null}
                {condition ? <li>Condition: {condition}</li> : null}
            </ul>

            <h6 className="title is-6">Functional network information</h6>
            <ul>
                {hasnetwork ? (
                    <React.Fragment>
                        <li>
                            <b>{formatNumber(gainmiles)}</b> miles could be gained by removing this barrier
                            <ul>
                                <li>{formatNumber(upstreammiles)} miles in the upstream network</li>
                                <li>{formatNumber(downstreammiles)} miles in the downstream network</li>
                            </ul>
                        </li>
                        <li>
                            <b>{sizeclasses}</b> river size {sizeclasses === 1 ? "class" : "classes"} could be gained by
                            removing this barrier
                        </li>
                        <li>
                            <b>{formatNumber(landcover, 0)}%</b> of the upstream floodplain is composed of natural
                            landcover
                        </li>
                        <li>
                            The upstream network has <b>{SINUOSITY[sinuosity]}</b> sinuosity
                        </li>
                    </React.Fragment>
                ) : (
                    <li className="has-text-grey">
                        This barrier is off-network and has no functional network information.
                    </li>
                )}
            </ul>

            <h6 className="title is-6">Species information</h6>
            <ul>
                {rarespp === null ? (
                    <li className="has-text-grey">
                        This barrier does not have subwatershed threatened and endangered aquatic species information.
                    </li>
                ) : (
                    <React.Fragment>
                        {rarespp > 0 ? (
                            <React.Fragment>
                                <li>
                                    <b>{rarespp}</b> threatened and endangered aquatic species have been found in the
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
                    </React.Fragment>
                )}
            </ul>

            <h6 className="title is-6">Feasibility of removal</h6>
            <ul>
                {potentialproject ? (
                    <li>{potentialproject}</li>
                ) : (
                    <li className="has-text-grey">No feasibility information is available for this barrier.</li>
                )}
            </ul>
        </div>
    )
}
BarrierDetails.propTypes = {
    lat: PropTypes.number.isRequired,
    lon: PropTypes.number.isRequired,
    hasnetwork: PropTypes.bool.isRequired,
    stream: PropTypes.string,
    basin: PropTypes.string,
    road: PropTypes.string,
    roadtype: PropTypes.string,
    crossingtype: PropTypes.string,
    condition: PropTypes.string,
    potentialproject: PropTypes.string,
    rarespp: PropTypes.number,
    gainmiles: PropTypes.number,
    upstreammiles: PropTypes.number,
    downstreammiles: PropTypes.number,
    sinuosity: PropTypes.number,
    landcover: PropTypes.number,
    sizeclasses: PropTypes.number
}

BarrierDetails.defaultProps = {
    stream: null,
    basin: null,
    road: null,
    roadtype: null,
    crossingtype: null,
    potentialproject: null,
    condition: null,
    rarespp: null,
    gainmiles: null,
    upstreammiles: null,
    downstreammiles: null,
    sinuosity: null,
    landcover: null,
    sizeclasses: null
}

export default BarrierDetails
