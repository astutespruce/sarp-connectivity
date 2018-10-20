import React from "react"
// import Map from "../Map"
import Sidebar from "../Map/Sidebar"

const Priority = () => (
    <React.Fragment>
        <Sidebar>sidebar content goes here</Sidebar>
        <div id="MapContainer">{/* <Map view="priority" /> */}</div>
    </React.Fragment>
)

export default Priority
