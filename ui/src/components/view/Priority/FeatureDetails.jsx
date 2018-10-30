import React from "react"
import PropTypes from "prop-types"

import { FeaturePropType } from "../../../CustomPropTypes"
import { SCENARIOS } from "../../map/config"

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

const FeatureDetails = ({ selectedFeature, onClose }) => {
    const { Barrier_Name: damName } = selectedFeature

    return (
        <React.Fragment>
            <div id="SidebarContent">
                <div id="SidebarHeader" className="flex-container flex-justify-center flex-align-start">
                    <div className="flex-grow">
                        <h3 className="title is-5">{damName ? standardizeName(damName) : "Unknown name"}</h3>
                    </div>
                    <div className="icon button" onClick={onClose}>
                        <span className="fa fa-times-circle is-size-4" />
                    </div>
                </div>

                <div id="SidebarContent" className="flex-container-column">
                    {Object.entries(SCENARIOS).map(([scenario, scenarioName]) => (
                        <div className="row flex-container flex-justify-space-between" key={scenario}>
                            <div className="field">{scenarioName} Tier</div>
                            <div>{selectedFeature[scenario]}</div>
                        </div>
                    ))}
                </div>
            </div>
        </React.Fragment>
    )
}

FeatureDetails.propTypes = {
    selectedFeature: FeaturePropType.isRequired,
    onClose: PropTypes.func.isRequired
}

export default FeatureDetails
