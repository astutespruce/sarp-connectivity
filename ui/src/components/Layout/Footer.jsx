import React from 'react'

import { Box, Flex } from 'theme-ui'
import { OutboundLink, Link } from 'components/Link'

import { siteMetadata } from 'constants'

const { version: dataVersion, date: dataDate } = siteMetadata

const Footer = () => (
  <Flex
    as="footer"
    sx={{
      flex: '0 0 auto',
      alignItems: 'center',
      justifyContent: 'space-between',
      py: '0.25rem',
      px: '0.5rem',
      color: '#FFF',
      bg: 'blue.9',
      fontSize: '0.7rem',
      a: {
        textDecoration: 'none',
        color: '#FFF',
      },
    }}
  >
    <Box>
      <OutboundLink to="https://southeastaquatics.net/">
        Southeast Aquatic Resources Partnership
      </OutboundLink>
      &nbsp;&nbsp;|&nbsp;&nbsp;
      <OutboundLink to="https://southeastaquatics.net/about/contact-us">
        Contact Us
      </OutboundLink>
      &nbsp;&nbsp;|&nbsp;&nbsp;
      <Link to="/terms">Terms of Use</Link>
    </Box>

    <Box>
      Data version: {dataVersion} ({dataDate})
    </Box>

    <Box>
      Created by{' '}
      <OutboundLink to="https://astutespruce.com">
        Astute Spruce, LLC
      </OutboundLink>
    </Box>
  </Flex>
)

export default Footer
