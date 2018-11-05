import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import Map from "./Map"
// import { LAYER_CONFIG } from "../../map/config"
import Sidebar from "../../Sidebar"
import { FeaturePropType } from "../../../CustomPropTypes"

const Heatmap = ({}) => (
    <React.Fragment>
        <Sidebar>TODO: content goes here</Sidebar>
        <div id="MapContainer">
            <Map />
        </div>
    </React.Fragment>
)

Heatmap.propTypes = {
    selectedFeature: FeaturePropType,
    layer: PropTypes.string,
    summaryUnits: ImmutablePropTypes.set.isRequired,

    setLayer: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired,
    selectUnit: PropTypes.func.isRequired
}

Heatmap.defaultProps = {
    selectedFeature: null,
    layer: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        system: state.get("system"),
        layer: state.get("layer"),
        selectedFeature: state.get("selectedFeature"),
        summaryUnits: state.get("summaryUnits")
    }
}

export default connect(
    mapStateToProps
    // actions
)(Heatmap)
