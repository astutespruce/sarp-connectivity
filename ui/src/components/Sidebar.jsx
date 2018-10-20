import React from "react"
import PropTypes from "prop-types"

const Sidebar = ({ children }) => (
    <div id="Sidebar" className="flex-container-column">
        {children}
    </div>
)

Sidebar.propTypes = {
    children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]).isRequired
}

Sidebar.defaultProps = {}

export default Sidebar
