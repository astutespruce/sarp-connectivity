import React from 'react'
import PropTypes from 'prop-types'

import { Box, Text } from 'theme-ui'

import { Link } from 'components/Link'

const NavMenuItem = ({
  label,
  url,
  inDevelopment,
  external,
  showBorder,
  hasChildren,
  ...props
}) => (
  <Box
    {...props}
    sx={{
      px: '1rem',
      py: '0.75rem',
      a: {
        color: 'grey.9',
        fontWeight: hasChildren ? 'bold' : 'inherit',
        outline: 'none !important',
      },
      '&:hover,&:focus-within': {
        bg: 'grey.0',
        a: {
          color: 'primary',
          textDecoration: 'none',
        },
      },
      '&:focus-within': {
        outlineStyle: 'auto',
        outlineWidth: '1px',
        outlineColor: 'purple.5   ',
      },
      '&:not(:first-of-type)': {
        borderTop: showBorder ? '1px solid' : 'inherit',
        borderTopColor: showBorder ? 'grey.1' : 'inherit',
      },
    }}
  >
    {url ? (
      <Link to={url} css={{ display: 'block' }}>
        {label}
        {inDevelopment ? (
          <Text sx={{ fontSize: 0, color: 'grey.8' }}>(in development)</Text>
        ) : null}
      </Link>
    ) : (
      <Text
        sx={{
          color: 'grey.7',
          fontStyle: 'italic',
        }}
      >
        {label}
        <Text sx={{ fontSize: 0 }}>(coming soon)</Text>
      </Text>
    )}
  </Box>
)

NavMenuItem.propTypes = {
  label: PropTypes.string.isRequired,
  url: PropTypes.string,
  inDevelopment: PropTypes.bool,
  external: PropTypes.bool,
  showBorder: PropTypes.bool,
  hasChildren: PropTypes.bool,
}

NavMenuItem.defaultProps = {
  url: null,
  inDevelopment: false,
  external: null,
  showBorder: true,
  hasChildren: false,
}

export default NavMenuItem
