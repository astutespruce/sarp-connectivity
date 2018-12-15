import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import * as actions from "../../../actions/summary"
import { FeaturePropType } from "../../../CustomPropTypes"
import { formatNumber } from "../../../utils/format"

import SummaryMap from "./Map"
import Sidebar from "../../Sidebar"
import SummaryUnitDetails from "./SummaryUnitDetails"

import summaryStats from "../../../data/summary_stats.json"

const Summary = ({ selectedFeature, type, selectFeature }) => {
    const { dams, barriers, miles } = summaryStats.southeast
    const total = type === "dams" ? dams : barriers

    return (
        <React.Fragment>
            <Sidebar>
                {selectedFeature === null ? (
                    <div id="SidebarContent">
                        <p className="is-size-5">
                            Across the Southeast, there are at least {formatNumber(dams)} dams, resulting in an average
                            of {formatNumber(miles)} miles of connected rivers and streams.
                            <br />
                            <br />
                            Click on a summary unit the map for more information about that area.
                        </p>
                        <p className="is-size-7 has-text-grey">
                            <br />
                            <br />
                            Note: These statistics are based on <i>inventoried</i> dams. Because the inventory is
                            incomplete in many areas, areas with a high number of dams may simply represent areas that
                            have a more complete inventory.
                        </p>
                    </div>
                ) : (
                    <SummaryUnitDetails
                        selectedFeature={selectedFeature}
                        total={total}
                        type={type}
                        meanConnectedMiles={miles}
                        onClose={() => selectFeature(null)}
                    />
                )}
            </Sidebar>
            <div id="MapContainer">
                <SummaryMap />
            </div>
        </React.Fragment>
    )
}

Summary.propTypes = {
    selectedFeature: FeaturePropType,
    type: PropTypes.string.isRequired,
    selectFeature: PropTypes.func.isRequired
}

Summary.defaultProps = {
    selectedFeature: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("summary")

    return {
        system: state.get("system"),
        type: state.get("type"),
        selectedFeature: state.get("selectedFeature")
    }
}

export default connect(
    mapStateToProps,
    actions
)(Summary)
