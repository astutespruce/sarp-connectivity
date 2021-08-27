import React from 'react'
import PropTypes from 'prop-types'

import { Box } from 'theme-ui'

const Section = ({ title, children, sx, ...props }) => (
  <Box
    as="section"
    {...props}
    sx={{
      mt: '1rem',
      '&:not(:first-of-type)': {
        mt: '1rem',
      },
      ...sx,
    }}
  >
    <Box
      {...props}
      sx={{
        fontWeight: 'bold',
        py: '0.25rem',
        px: '1rem',
        bg: 'grey.1',
        ...sx,
      }}
    >
      {title}
    </Box>
    <Box sx={{ pl: '1rem', mt: '0.5rem' }}>{children}</Box>
  </Box>
)

Section.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  sx: PropTypes.object,
}

Section.defaultProps = {
  sx: {},
}

export default Section
