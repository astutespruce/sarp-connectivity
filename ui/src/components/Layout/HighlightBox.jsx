import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Heading, Text } from 'theme-ui'

import { Icon } from 'components/Icon'

const HighlightBox = ({ icon, title, children, ...props }) => (
  <Box
    sx={{
      flex: '1 0 auto',
      p: '1rem',
      bg: 'blue.100',
      borderRadius: '0.5rem',
    }}
    {...props}
  >
    <Flex
      sx={{
        alignItems: 'center',
        mb: '0.5rem',
        pb: '0.5rem',
        borderBottom: '4px solid #FFF',
      }}
    >
      {icon ? <Icon name={icon} size="4rem" mr="0.25rem" /> : null}
      <Heading
        as="h3"
        sx={{
          flex: '1 1 auto',
          m: 0,
          fontWeight: 'normal',
          textAlign: icon ? 'unset' : 'center',
        }}
      >
        {title}
      </Heading>
    </Flex>
    <Box
      sx={{
        fontSize: '1.05em',
        lineHeight: 1.5,
        color: 'blue.9',
      }}
    >
      {children}
    </Box>
  </Box>
)

HighlightBox.propTypes = {
  icon: PropTypes.string,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
}

HighlightBox.defaultProps = {
  icon: null,
}

export default HighlightBox
