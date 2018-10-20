import React from "react"
import { connect } from "react-redux"

import * as actions from "../../actions/priority"
import PriorityMap from "../Map/PriorityMap"
import Sidebar from "../Sidebar"

const Priority = () => (
    <React.Fragment>
        <Sidebar>TODO: sidebar content goes here</Sidebar>
        <div id="MapContainer">
            <PriorityMap />
        </div>
    </React.Fragment>
)

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
