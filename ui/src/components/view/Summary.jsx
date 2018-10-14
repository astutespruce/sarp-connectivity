import React from "react"
import Map from "../Map"
import Sidebar from "../Map/Sidebar"

const Summary = () => (
    <React.Fragment>
        <Sidebar>sidebar content goes here</Sidebar>
        <div id="MapContainer">
            <Map view="summary" />
        </div>
    </React.Fragment>
)

export default Summary
