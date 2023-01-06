import React from 'react'
import PropTypes from 'prop-types'
import { ExternalLinkAlt } from '@emotion-icons/fa-solid'
import { Flex, Box } from 'theme-ui'

import OutboundLink from './OutboundLink'

const ExternalLink = ({ to, children }) => (
  <OutboundLink to={to}>
    <Flex sx={{ lineHeight: 1 }}>
      <Box sx={{ mr: '0.5em' }}>{children}</Box>
      <Box sx={{ flex: '0 0 auto', opacity: '0.5', mt: '-2px' }}>
        <ExternalLinkAlt size="1em" />
      </Box>
    </Flex>
  </OutboundLink>
)

ExternalLink.propTypes = {
  to: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.Node),
  ]).isRequired,
}

export default ExternalLink
