import React, { Component } from "react"
import { NavLink, Link } from "react-router-dom"
import { ReactComponent as Logo } from "../img/logo.svg"

class NavBar extends Component {
    constructor(props) {
        super(props)

        this.state = {
            isActive: false
        }
    }

    render() {
        const { isActive } = this.state

        return (
            <nav className="navbar">
                <div className="navbar-brand">
                    <Link
                        to="/"
                        style={{ flexGrow: 1 }}
                        onClick={() => {
                            this.setState({ isActive: false })
                        }}
                    >
                        <div className="navbar-item">
                            <Logo className="logo" />
                            <h1 className="is-size-4 is-size-5-mobile has-text-white has-text-weight-bold">
                                Southeast Aquatic Barrier Inventory Visualization and Prioritization Tool
                            </h1>
                        </div>
                    </Link>
                    <button
                        type="button"
                        className={`button navbar-burger has-text-white ${isActive ? "is-active" : ""}`}
                        onClick={() => {
                            this.setState({ isActive: !isActive })
                        }}
                    >
                        <span />
                        <span />
                        <span />
                    </button>
                </div>
                <div className={`navbar-menu ${isActive ? "is-active" : ""}`}>
                    <div
                        className="navbar-end"
                        onClick={() => {
                            this.setState({ isActive: false })
                        }}
                    >
                        <NavLink to="/compare" className="navbar-item has-text-white">
                            <span className="fa fa-sliders" />
                            <span>TODO</span>
                        </NavLink>
                        <NavLink to="/explore" className="navbar-item has-text-white">
                            <span className="fa fa-binoculars" />
                            <span>TODO</span>
                        </NavLink>
                    </div>
                </div>
            </nav>
        )
    }
}

NavBar.defaultProps = {}

export default NavBar
