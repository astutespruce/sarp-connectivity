import React from "react"

import Intro from "./Intro"
import Tool from "./Tool"
import Inventory from "./Inventory"
import UseCases from "./UseCases"
import Concepts from "./Concepts"
import Background from "./Background"
import SARP from "./SARP"
import Credits from "./Credits"

const Home = () => (
    <div id="Home" className="view">
        <Intro />

        <Tool />

        <Inventory />

        <UseCases />

        <Concepts />

        <Background />

        <SARP />

        <Credits />
    </div>
)

export default Home
