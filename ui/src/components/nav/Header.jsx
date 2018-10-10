import React from "react"
// import PropTypes from 'prop-types'
import { Link, NavLink } from "react-router-dom"

import { ReactComponent as Logo } from "../../img/logo.svg"

const Header = () => (
    <nav className="flex-container flex-justify-space-between flex-align-center">
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
            <NavLink to="/summary" className="has-text-white nav-link">
                <span className="fa fa-chart-bar" />
                <span>Summarize</span>
            </NavLink>
            <NavLink to="/priority" className="has-text-white nav-link">
                <span className="fa fa-search-location" />
                <span>Prioritize</span>
            </NavLink>
        </div>
    </nav>
)

export default Header

// class NavBar extends Component {
//     constructor(props) {
//         super(props)

//         this.state = {
//             isActive: false
//         }
//     }

//     render() {
//         const { isActive } = this.state

//         return (
//             <nav className="navbar">
//                 <div className="navbar-brand">
//                     <Link
//                         to="/"
//                         style={{ flexGrow: 1 }}
//                         onClick={() => {
//                             this.setState({ isActive: false })
//                         }}
//                     >
//                         <div className="navbar-item">
//                             <Logo className="logo" />
//                             <h1 className="is-size-4 is-size-5-mobile has-text-white has-text-weight-bold">
//                                 Southeast Aquatic Barrier Inventory Visualization and Prioritization Tool
//                             </h1>
//                         </div>
//                     </Link>
//                     <button
//                         type="button"
//                         className={`button navbar-burger has-text-white ${isActive ? "is-active" : ""}`}
//                         onClick={() => {
//                             this.setState({ isActive: !isActive })
//                         }}
//                     >
//                         <span />
//                         <span />
//                         <span />
//                     </button>
//                 </div>
//                 <div className={`navbar-menu ${isActive ? "is-active" : ""}`}>
//                     <div
//                         className="navbar-end"
//                         onClick={() => {
//                             this.setState({ isActive: false })
//                         }}
//                     >
//                         <NavLink to="/compare" className="navbar-item has-text-white">
//                             <span className="fa fa-sliders" />
//                             <span>TODO</span>
//                         </NavLink>
//                         <NavLink to="/explore" className="navbar-item has-text-white">
//                             <span className="fa fa-binoculars" />
//                             <span>TODO</span>
//                         </NavLink>
//                     </div>
//                 </div>
//             </nav>
//         )
//     }
// }

// NavBar.defaultProps = {}

// export default NavBar
