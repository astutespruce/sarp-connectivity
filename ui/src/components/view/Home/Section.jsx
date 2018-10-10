import React from "react"
import PropTypes from "prop-types"

const Section = ({ children }) => <section>{children}</section>

Section.propTypes = {
    children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]).isRequired
}

export default Section
