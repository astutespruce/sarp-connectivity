import React from "react"
import PropTypes from "prop-types"

import { FeaturePropType } from "../CustomPropTypes"
import { formatNumber, formatPercent } from "../utils/format"

import { LAYER_CONFIG } from "./Map/config"

import summaryStats from "../data/summary_stats.json"

const SummaryUnitDetails = ({ selectedFeature, totalDams, meanConnectedMiles, summaryStats, onClose }) => {
    const { id, layerId, name, dams, connectedmiles } = selectedFeature.toJS()
    const layerConfig = LAYER_CONFIG.filter(({ id: lyrID }) => lyrID === layerId)[0]
    const { title: layerTitle } = layerConfig

    const percentDams = (100 * dams) / totalDams
    const milesCompare = connectedmiles - meanConnectedMiles

    const title = layerId === "states" ? id : `${layerTitle}: ${name || id}`

    return (
        <React.Fragment>
            <div id="SidebarHeader" className="flex-container flex-justify-center flex-align-start">
                <div className="flex-grow">
                    <h3 className="title is-5">{title}</h3>
                </div>
                <div className="icon button" onClick={onClose}>
                    <span className="fa fa-times-circle is-size-4" />
                </div>
            </div>
            <div id="SidebarContent" className="flex-container-column">
                <p className="is-size-5">
                    This area contains at least {formatNumber(dams, 0)} dams that have been inventoried so far,
                    resulting in an average of {formatNumber(connectedmiles)} miles of connected rivers.
                    <br />
                    <br />
                    This area has {formatPercent(percentDams)}% of the inventoried dams in the Southeast and{" "}
                    {formatNumber(Math.abs(milesCompare))} {milesCompare > 0 ? "more" : "less"} miles of connected river
                    network than the average for the region.
                </p>
                <p className="is-size-7 has-text-grey">
                    <br />
                    <br />
                    Note: These statistics are based on <i>inventoried</i> dams. Because the inventory is incomplete in
                    many areas, areas with a high number of dams may simply represent areas that have a more complete
                    inventory.
                </p>
            </div>
        </React.Fragment>
    )
}

SummaryUnitDetails.propTypes = {
    selectedFeature: FeaturePropType.isRequired,
    onClose: PropTypes.func.isRequired,
    totalDams: PropTypes.number.isRequired,
    meanConnectedMiles: PropTypes.number.isRequired,
    summaryStats: PropTypes.object
}

SummaryUnitDetails.defaultProps = {
    summaryStats
}

export default SummaryUnitDetails
