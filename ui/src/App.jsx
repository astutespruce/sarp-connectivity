import React from "react"
import { Route } from "react-router-dom"

import Header from "./components/nav/Header"
import Footer from "./components/nav/Footer"
import Home from "./components/view/Home"
import Download from "./components/view/Download"

const App = () => (
    <div className="flex-column full-height">
        <Header />
        <div className="main">
            <Route exact path="/" component={Home} />
            <Route exact path="/download" component={Download} />
            {/* <Route path="/:anything" render={() => this.renderMapView()} /> */}
        </div>
        <Footer />
    </div>
)

export default App
