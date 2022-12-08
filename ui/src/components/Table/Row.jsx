import React from 'react'
import PropTypes from 'prop-types'
import { Grid } from 'theme-ui'

const Row = ({ children, sx, ...props }) => (
  <Grid
    columns={children.length}
    {...props}
    sx={{
      '&:not(:first-of-type)': {
        mt: '0.25em',
        pt: '0.25em',
        borderTop: '1px solid',
        borderTopColor: 'grey.2',
      },
      ...sx,
    }}
  >
    {children}
  </Grid>
)

Row.propTypes = {
  children: PropTypes.arrayOf(PropTypes.node).isRequired,
  sx: PropTypes.object,
}

Row.defaultProps = {
  sx: {},
}

export default Row
