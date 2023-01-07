import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import NavMenuItem from './NavMenuItem'

const NavMenu = ({ label, items, ...props }) => (
  <Box
    {...props}
    tabIndex={0}
    as="ul"
    sx={{
      zIndex: 10000,
      position: 'relative',
      cursor: 'pointer',
      listStyle: 'none',
      flex: '0 1 auto',
      m: 0,
      p: 0,
      '&:hover > li': {
        bg: 'blue.8',
      },
      '&:hover li ul, &:focus-within li ul': {
        display: 'block',
      },
    }}
  >
    <Box
      as="li"
      sx={{
        alignItems: 'center',
        borderRadius: '6px 6px 0 0',
        borderTop: '1px solid transparent',
        borderLeft: '1px solid transparent',
        borderRight: '1px solid transparent',
        position: 'relative',
        transformStyle: 'preserve-3d',
        mr: '0.5rem',
      }}
    >
      <Text
        sx={{
          color: '#FFF',
          py: '0.25rem',
          px: '0.5rem',
        }}
      >
        {label}
      </Text>
      <Box
        as="ul"
        sx={{
          bg: '#FFF',
          borderTop: '4px solid',
          borderTopColor: 'primary',
          p: 0,
          listStyle: 'none',
          boxShadow: '1px 1px 6px #333',
          position: 'absolute',
          width: ['100%'],
          minWidth: ['100%', '300px'],
          zIndex: 1,
          display: 'none',
          right: '-1px',
        }}
      >
        {items.map((item) => (
          <NavMenuItem key={item.url} {...item} />
        ))}
      </Box>
    </Box>
  </Box>
)

NavMenu.propTypes = {
  label: PropTypes.string.isRequired,
  items: PropTypes.arrayOf(PropTypes.shape(NavMenuItem.propTypes)).isRequired,
}

export default NavMenu
