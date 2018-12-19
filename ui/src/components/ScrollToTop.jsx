/**
 * Lightweight component to force scrolling to the top of the content on route change
 */

import React, { Component } from "react"
import PropTypes from "prop-types"
import { withRouter } from "react-router"

class ScrollToTop extends Component {
    componentDidUpdate({ location: { pathname: prevPath } }) {
        const {
            location: { pathname }
        } = this.props

        console.log("path changed", prevPath, "=>", pathname)

        if (pathname !== prevPath) {
            const elem = document.getElementById("ContentPage")
            if (elem) {
                elem.scrollIntoView()
            }
        }
    }

    render() {
        const { children } = this.props
        return children
    }
}

ScrollToTop.propTypes = {
    location: PropTypes.shape({
        pathname: PropTypes.string.isRequired
    }).isRequired,
    children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]).isRequired
}

export default withRouter(ScrollToTop)
