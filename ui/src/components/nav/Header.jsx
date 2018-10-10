import React from "react"
// import PropTypes from 'prop-types'
import { Link, NavLink } from "react-router-dom"

import { ReactComponent as Logo } from "../../img/logo.svg"

const Header = () => (
    <header className="flex-container flex-justify-space-between flex-align-center">
        <div>
            <Link to="/" style={{ flexGrow: 1 }} className="flex-container flex-justify-start">
                <Logo className="logo" />
                <h1 className="is-size-4 is-hidden-touch has-text-white has-text-weight-bold">
                    Southeast Aquatic Barrier Inventory Prioritization Tool
                </h1>
                <h1 className="is-size-5 is-hidden-desktop has-text-white has-text-weight-bold">
                    Southeast Aquatic Barrier Tool
                </h1>
            </Link>
        </div>
        <div className="flex-container flex-justify-end">
            <NavLink to="/summary" activeClassName="active" className="has-text-white nav-link">
                <span className="fa fa-chart-bar" />
                <span>Summarize</span>
            </NavLink>
            <NavLink to="/priority" activeClassName="active" className="has-text-white nav-link">
                <span className="fa fa-search-location" />
                <span>Prioritize</span>
            </NavLink>
        </div>
    </header>
)

export default Header
