import React from "react"
import { connect } from "react-redux"

import * as actions from "../../actions"
import PriorityMap from "../Map/PriorityMap"
import Sidebar from "../Map/Sidebar"

const Priority = () => (
    <React.Fragment>
        <Sidebar>sidebar content goes here</Sidebar>
        <div id="MapContainer">
            <PriorityMap />
        </div>
    </React.Fragment>
)

const mapStateToProps = state => ({ system: state.get("system"), selectedFeature: state.get("selectedFeature") })

export default connect(
    mapStateToProps,
    actions
)(Priority)
