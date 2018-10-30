import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
import Map from "./Map"
// import { LAYER_CONFIG } from "../../map/config"
import Sidebar from "../../Sidebar"
import { FeaturePropType } from "../../../CustomPropTypes"

import FeatureDetails from "./FeatureDetails"
import SummaryLayerChooser from "./SummaryLayerChooser"
import SummaryUnitChooser from "./SummaryUnitChooser"

const Priority = ({ selectedFeature, layer, summaryUnits, setLayer, selectFeature, selectUnit }) => {
    let content = null
    if (selectedFeature !== null) {
        content = <FeatureDetails selectedFeature={selectedFeature} onClose={() => selectFeature(null)} />
    } else if (layer !== null) {
        content = (
            <SummaryUnitChooser
                summaryUnits={summaryUnits}
                onDeselectUnit={id => selectUnit(id)}
                onBack={() => setLayer(null)}
            />
        )
    } else {
        content = <SummaryLayerChooser onSelect={setLayer} />
    }

    return (
        <React.Fragment>
            <Sidebar>{content}</Sidebar>
            <div id="MapContainer">
                <Map />
            </div>
        </React.Fragment>
    )
}

Priority.propTypes = {
    selectedFeature: FeaturePropType,
    layer: PropTypes.string,
    summaryUnits: ImmutablePropTypes.set.isRequired,

    setLayer: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired,
    selectUnit: PropTypes.func.isRequired
}

Priority.defaultProps = {
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
    mapStateToProps,
    actions
)(Priority)
