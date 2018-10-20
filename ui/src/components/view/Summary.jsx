import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import * as actions from "../../actions"
import { FeaturePropType } from "../../CustomPropTypes"
import { formatNumber } from "../../utils/format"

import SummaryMap from "../Map/SummaryMap"
import Sidebar from "../Sidebar"
import SummaryUnitDetails from "../SummaryUnitDetails"

import summaryStats from "../../data/summary_stats.json"

const Summary = ({ selectedFeature, dams, connectedmiles, selectFeature }) => (
    <React.Fragment>
        <Sidebar>
            {selectedFeature === null ? (
                <div id="SidebarContent">
                    <p className="is-size-5">
                        Across the Southeast, there are at least {formatNumber(dams)} dams, resulting in an average of{" "}
                        {formatNumber(connectedmiles)} miles of connected rivers.
                    </p>
                    <p className="is-size-7 has-text-grey">
                        <br />
                        <br />
                        Note: These statistics are based on <i>inventoried</i> dams. Because the inventory is incomplete
                        in many areas, areas with a high number of dams may simply represent areas that have a more
                        complete inventory.
                    </p>
                </div>
            ) : (
                <SummaryUnitDetails
                    selectedFeature={selectedFeature}
                    totalDams={dams}
                    meanConnectedMiles={connectedmiles}
                    onClose={() => selectFeature(null)}
                />
            )}
        </Sidebar>
        <div id="MapContainer">
            <SummaryMap />
        </div>
    </React.Fragment>
)

Summary.propTypes = {
    selectedFeature: FeaturePropType,
    dams: PropTypes.number,
    connectedmiles: PropTypes.number,

    selectFeature: PropTypes.func.isRequired
}

Summary.defaultProps = {
    selectedFeature: null,
    dams: summaryStats.sarp.dams,
    connectedmiles: summaryStats.sarp.connectedmiles
}

const mapStateToProps = state => ({ system: state.get("system"), selectedFeature: state.get("selectedFeature") })

export default connect(
    mapStateToProps,
    actions
)(Summary)
