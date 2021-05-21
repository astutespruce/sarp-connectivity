import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

const Tab = ({ id, children, sx }) => (
  <Box id={id} sx={{ flex: '1 1 auto', p: '1rem', overflowY: 'auto', ...sx }}>
    {children}
  </Box>
)

Tab.propTypes = {
  id: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.element,
    PropTypes.array,
  ]).isRequired,
  sx: PropTypes.object,
}

Tab.defaultProps = {
  sx: {},
}

export default Tab
