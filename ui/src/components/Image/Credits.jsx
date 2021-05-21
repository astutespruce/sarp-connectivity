import React from 'react'
import PropTypes from 'prop-types'
import { Box, NavLink } from 'theme-ui'

import { OutboundLink } from 'components/Link'

const Credits = ({ author, url, caption }) => (
  <Box
    sx={{
      fontSize: 'smaller',
      textAlign: 'right',
      position: 'absolute',
      bottom: 0,
      right: 0,
      zIndex: 3,
      color: 'grey.3',
      py: '0.25rem',
      px: '0.5rem',
      textShadow: '1px 1px 3px #000',
      bg: 'rgba(0,0,0,0.7)',
      a: {
        color: 'grey.3',
        textDecoration: 'none',
      },
    }}
  >
    {caption ? `${caption} | ` : null}
    Photo:&nbsp;
    {url ? <OutboundLink to={url}>{author}</OutboundLink> : author}
  </Box>
)

Credits.propTypes = {
  author: PropTypes.string.isRequired,
  url: PropTypes.string,
  caption: PropTypes.string,
}

Credits.defaultProps = {
  url: NavLink,
  caption: null,
}

export default Credits
