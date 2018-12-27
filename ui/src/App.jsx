import React from "react"
import { Route, Switch } from "react-router-dom"

import Header from "./components/nav/Header"
import Footer from "./components/nav/Footer"
import Home from "./components/view/Home"
import Download from "./components/view/Download"
import Priority from "./components/view/Priority"
import Summary from "./components/view/Summary"

import NetworkLength from "./components/view/metrics/NetworkLength"
import NetworkComplexity from "./components/view/metrics/NetworkComplexity"
import NetworkSinuosity from "./components/view/metrics/NetworkSinuosity"
import NaturalLandcover from "./components/view/metrics/NaturalLandcover"

import NotFound from "./components/view/NotFound"

const App = () => (
    <div className="flex-container-column full-height fill-viewport">
        <Header />
        <div className="main">
            <Switch>
                <Route exact path="/" component={Home} />
                <Route exact path="/download" component={Download} />
                <Route exact path="/summary" component={Summary} />
                <Route exact path="/priority" component={Priority} />

                <Route exact path="/metrics/length" component={NetworkLength} />
                <Route exact path="/metrics/complexity" component={NetworkComplexity} />
                <Route exact path="/metrics/sinuosity" component={NetworkSinuosity} />
                <Route exact path="/metrics/landcover" component={NaturalLandcover} />

                {/* Fall-through route */}
                <Route component={NotFound} />
            </Switch>
        </div>
        <Footer />
    </div>
)

export default App
