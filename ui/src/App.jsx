import React from "react"
import { Route, Switch } from "react-router-dom"

import Header from "./components/nav/Header"
import Footer from "./components/nav/Footer"
import Home from "./components/view/Home"
import Download from "./components/view/Download"
// import Priority from "./components/view/Priority"
import PrioritizeStart from "./components/view/Priority/Start"
import Summary from "./components/view/Summary"
import TestFilter from "./test/TestFilter"
import NotFound from "./components/view/NotFound"
// import Find from "./components/view/Find"

// testing
import Heatmap from "./components/view/Heatmap"

const App = () => (
    <div className="flex-container-column full-height fill-viewport">
        <Header />
        <div className="main">
            <Switch>
                <Route exact path="/" component={Home} />
                <Route exact path="/download" component={Download} />
                <Route exact path="/summary" component={Summary} />
                <Route exact path="/priority" component={PrioritizeStart} />

                {/* FIXME! */}
                {/* <Route exact path="/find" component={Find} /> */}
                <Route exact path="/test" component={TestFilter} />

                <Route exact path="/heatmap" component={Heatmap} />

                {/* Fall-through route */}
                <Route component={NotFound} />
            </Switch>
        </div>
        <Footer />
    </div>
)

export default App
