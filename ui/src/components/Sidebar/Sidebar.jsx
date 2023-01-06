import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex } from 'theme-ui'

const Sidebar = ({ children, allowScroll }) => (
  <Box
    sx={{
      width: ['100%', '27rem'],
      flex: '0 0 auto',
      borderRight: '1px solid',
      borderRightColor: 'grey.8',
      height: '100%',
    }}
  >
    <Flex
      sx={{
        flexDirection: 'column',
        flex: '1 1 auto',
        overflowX: 'hidden',
        overflowY: allowScroll ? 'auto' : 'hidden',
        height: '100%',
      }}
    >
      {children}
    </Flex>
  </Box>
)

Sidebar.propTypes = {
  children: PropTypes.node.isRequired,
  allowScroll: PropTypes.bool,
}

Sidebar.defaultProps = {
  allowScroll: false,
}

export default Sidebar
