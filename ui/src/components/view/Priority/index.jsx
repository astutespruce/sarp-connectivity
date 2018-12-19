import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"
import Start from "./Start"
import Map from "./Map"
import Sidebar from "../../Sidebar"
import { FeaturePropType } from "../../../CustomPropTypes"

// import FeatureDetails from "./FeatureDetails"
import Barrier from "../../barriers/Barrier"
import SummaryLayerChooser from "./SummaryLayerChooser"
import SummaryUnitChooser from "./SummaryUnitChooser"

const Priority = ({
    type,
    mode,
    selectedFeature,
    layer,
    summaryUnits,
    setLayer,
    selectFeature,
    selectUnit,
    setType,
    setMode,
    fetchRanks
}) => {
    let content = null

    if (selectedFeature !== null) {
        content = <Barrier barrier={selectedFeature.toJS()} onClose={() => selectFeature(null)} />
    } else {
        switch (mode) {
            case "select": {
                if (layer === null) {
                    content = <SummaryLayerChooser onSelect={setLayer} onBack={() => setMode("default")} />
                } else {
                    content = (
                        <SummaryUnitChooser
                            summaryUnits={summaryUnits}
                            onDeselectUnit={id => selectUnit(id)}
                            onBack={() => setLayer(null)}
                            // onSubmit={() => setMode("prioritize")}
                            onSubmit={() => fetchRanks(layer, summaryUnits.toJS())}
                        />
                    )
                }
                break
            }
            case "prioritize": {
                content = (
                    <div id="SidebarContent">
                        <a href="#" onClick={() => setMode("select")}>
                            <span className="fa fa-reply" />
                            &nbsp; select other summary units
                        </a>
                        <p>TODO: show priorities on map and summary info here</p>
                        <button type="button" className="button" onClick={() => setMode("default")}>
                            start over
                        </button>
                    </div>
                )
                break
            }
        }
    }

    // content = <FeatureDetails selectedFeature={selectedFeature} onClose={() => selectFeature(null)} />

    return (
        <React.Fragment>
            {type === null ? (
                <Start setType={setType} />
            ) : (
                <React.Fragment>
                    <Sidebar>{content}</Sidebar>
                    <div id="MapContainer">
                        <Map />
                    </div>
                </React.Fragment>
            )}
        </React.Fragment>
    )
}

Priority.propTypes = {
    type: PropTypes.string,
    mode: PropTypes.string.isRequired,
    selectedFeature: FeaturePropType,
    layer: PropTypes.string,
    summaryUnits: ImmutablePropTypes.set.isRequired,

    setType: PropTypes.func.isRequired,
    setLayer: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired,
    selectUnit: PropTypes.func.isRequired,
    setMode: PropTypes.func.isRequired,
    fetchRanks: PropTypes.func.isRequired
}

Priority.defaultProps = {
    type: null,
    selectedFeature: null,
    layer: null
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        type: state.get("type"),
        mode: state.get("mode"),
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
