import React from "react"

import Histogram from "../components/view/Priority/Histogram"
import Sidebar from "../components/Sidebar"

const counts = [1, 0, 1, 8, 24, 32, 36, 32, 47, 54, 58, 58, 58, 65, 62, 90, 55, 28, 17, 19]

const TestHistogram = () => (
    <Sidebar>
        <Histogram counts={counts} type="dams" />
    </Sidebar>
)

export default TestHistogram
