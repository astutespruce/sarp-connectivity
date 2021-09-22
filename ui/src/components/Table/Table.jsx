import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

const Table = ({ columns, children, sx, ...props }) => (
  <Box
    {...props}
    sx={{
      '& > div': { gridTemplateColumns: columns },
      ...sx,
    }}
  >
    {children}
  </Box>
)

Table.propTypes = {
  columns: PropTypes.string.isRequired,
  children: PropTypes.arrayOf(PropTypes.node).isRequired,
  sx: PropTypes.object,
}

Table.defaultProps = {
  sx: {},
}

export default Table
