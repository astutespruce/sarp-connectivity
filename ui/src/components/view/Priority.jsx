import React from "react"
import { connect } from "react-redux"

import * as actions from "../../actions/priority"
import PriorityMap from "../map/PriorityMap"
import { SCENARIOS } from "../map/config"
import Sidebar from "../Sidebar"
import { FeaturePropType } from "../../CustomPropTypes"

/**
 * If name is all uppercase coming in and is more than 3 characters, title case it instead
 * @param {String} name
 */
const standardizeName = name => {
    if (name === name.toUpperCase() && name.length > 3) {
        return name
            .split(" ")
            .map(s => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase())
            .join(" ")
    }
    return name
}
window.std = standardizeName

const FeatureDetails = ({ selectedFeature }) => {
    const { Barrier_Name: damName } = selectedFeature

    return (
        <div id="SidebarContent">
            <h5 className="is-size-5">{damName ? standardizeName(damName) : "Unknown name"}</h5>
            {Object.entries(SCENARIOS).map(([scenario, scenarioName]) => (
                <div className="row flex-container flex-justify-space-between" key={scenario}>
                    <div className="field">{scenarioName} Tier</div>
                    <div>{selectedFeature[scenario]}</div>
                </div>
            ))}
        </div>
    )
}

FeatureDetails.propTypes = {
    selectedFeature: FeaturePropType.isRequired
}

const Priority = ({ selectedFeature }) => (
    <React.Fragment>
        <Sidebar>
            {selectedFeature === null ? (
                <div id="SidebarContent">
                    <p className="is-size-5">Click on a dam on the map for more information.</p>
                </div>
            ) : (
                <FeatureDetails selectedFeature={selectedFeature} />
            )}
        </Sidebar>
        <div id="MapContainer">
            ]<PriorityMap />
        </div>
    </React.Fragment>
)

Priority.propTypes = {
    selectedFeature: FeaturePropType
}

Priority.defaultProps = {
    selectedFeature: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        system: state.get("system"),
        selectedFeature: state.get("selectedFeature")
    }
}

export default connect(
    mapStateToProps,
    actions
)(Priority)
