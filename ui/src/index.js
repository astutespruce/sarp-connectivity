import React from "react"
import ReactDOM from "react-dom"
// import { init } from "@sentry/browser"
// import ReactGA from "react-ga"
import { createLogger } from "redux-logger"
import { createStore, applyMiddleware } from "redux"
import { Provider } from "react-redux"
import { BrowserRouter as Router } from "react-router-dom"

import reducer from "./reducers"

import "bulma/css/bulma.css"
import "./main.css"

import App from "./App"

// Setup sentry and Google Analytics
// TODO: do this only in production enviroment
// init({
//     dsn: "https://7e21a171129a43c9a87c650572cd8265@sentry.io/1297029"
// })

// ReactGA.initialize("UA-82274034-8")

const store = createStore(reducer, applyMiddleware(createLogger()))

/* eslint-disable react/jsx-filename-extension */
ReactDOM.render(
    <Provider store={store}>
        <Router>
            <App />
        </Router>
    </Provider>,
    document.getElementById("Root")
)
