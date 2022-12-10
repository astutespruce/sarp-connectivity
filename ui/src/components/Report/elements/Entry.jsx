import React from 'react'
import PropTypes from 'prop-types'

const Entry = ({ children }) => <>{children}</>

Entry.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
}

export default Entry
