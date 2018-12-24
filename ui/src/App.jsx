import React from "react"
import { Route, Switch } from "react-router-dom"

import Header from "./components/nav/Header"
import Footer from "./components/nav/Footer"
import Home from "./components/view/Home"
import Download from "./components/view/Download"
import Priority from "./components/view/Priority"
import Summary from "./components/view/Summary"
import NotFound from "./components/view/NotFound"

// testing
import Heatmap from "./components/view/Heatmap"
import TestHistogram from "./test/TestHistogram"

const App = () => (
    <div className="flex-container-column full-height fill-viewport">
        <Header />
        <div className="main">
            <Switch>
                <Route exact path="/" component={Home} />
                <Route exact path="/download" component={Download} />
                <Route exact path="/summary" component={Summary} />
                <Route exact path="/priority" component={Priority} />

                {/* FIXME! */}
                <Route exact path="/test" component={TestHistogram} />

                <Route exact path="/heatmap" component={Heatmap} />

                {/* Fall-through route */}
                <Route component={NotFound} />
            </Switch>
        </div>
        <Footer />
    </div>
)

export default App
