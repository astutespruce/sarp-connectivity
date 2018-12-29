/* eslint-disable react/jsx-filename-extension */

import React from "react"
import ReactDOM from "react-dom"
// import { init } from "@sentry/browser"
import ReactGA from "react-ga"
import Raven from "raven-js"
import thunkMiddleware from "redux-thunk"
import { createLogger } from "redux-logger"
import { createStore, applyMiddleware } from "redux"
import { Provider } from "react-redux"
// import { BrowserRouter as Router } from "react-router-dom"
import { createBrowserHistory } from "history"
import { ConnectedRouter, routerMiddleware } from "connected-react-router/immutable"

import rootReducer from "./reducers"
import trackingMiddleware from "./analytics"

import "@fortawesome/fontawesome-free/css/all.min.css"
import "bulma/css/bulma.css"
import "./main.css"

import App from "./App"

// Setup history
const history = createBrowserHistory()

// Setup sentry and Google Analytics
const { NODE_ENV, REACT_APP_GOOGLE_ANALYTICS, REACT_APP_SENTRY_DSN } = process.env
if (NODE_ENV === "development") {
    // FIXME: production
    if (REACT_APP_GOOGLE_ANALYTICS) {
        ReactGA.initialize(REACT_APP_GOOGLE_ANALYTICS)
    }
    if (REACT_APP_SENTRY_DSN) {
        Raven.config(REACT_APP_SENTRY_DSN).install()
    }
}

const middleware = [thunkMiddleware, routerMiddleware(history), trackingMiddleware]

// TODO: only for development
if (NODE_ENV === "development") {
    const logger = createLogger({
        stateTransformer: state => state.toJS()
    })
    middleware.push(logger)
}

const store = createStore(rootReducer(history), applyMiddleware(...middleware))

ReactDOM.render(
    <Provider store={store}>
        <ConnectedRouter history={history}>
            <App />
        </ConnectedRouter>
    </Provider>,
    document.getElementById("Root")
)
