/* eslint-disable react/jsx-filename-extension */

import React from "react"
import ReactDOM from "react-dom"
// import { init } from "@sentry/browser"
// import ReactGA from "react-ga"
import thunkMiddleware from "redux-thunk"
import { createLogger } from "redux-logger"
import { createStore, applyMiddleware } from "redux"
import { Provider } from "react-redux"
import { BrowserRouter as Router } from "react-router-dom"
import { combineReducers } from "redux-immutable"

import ScrollToTop from "./components/ScrollToTop"

import { summaryReducer, priorityReducer, detailsReducer } from "./reducers"

import "@fortawesome/fontawesome-free/css/all.min.css"
import "bulma/css/bulma.css"
import "./main.css"

import App from "./App"

// Setup sentry and Google Analytics
// TODO: do this only in production enviroment
// init({
//     dsn: "https://7e21a171129a43c9a87c650572cd8265@sentry.io/1297029"
// })

// ReactGA.initialize("UA-82274034-8")

// TODO: only for development
const logger = createLogger({
    stateTransformer: state => state.toJS()
})

const rootReducer = combineReducers({
    priority: priorityReducer,
    summary: summaryReducer,
    details: detailsReducer
})

const store = createStore(rootReducer, applyMiddleware(thunkMiddleware, logger))

ReactDOM.render(
    <Provider store={store}>
        <Router>
            <ScrollToTop>
                <App />
            </ScrollToTop>
        </Router>
    </Provider>,
    document.getElementById("Root")
)
