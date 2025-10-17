import React from 'react'
import { Box, Heading, Paragraph } from 'theme-ui'

import { siteMetadata } from 'config'
import { OutboundLink } from 'components/Link'

const { naccURL } = siteMetadata

const GetInvolvedSection = () => (
  <Box variant="boxes.section">
    <Box>
      <Heading as="h2" sx={{ fontWeight: 'normal' }}>
        Get involved!
      </Heading>
      <Paragraph sx={{ mt: '1rem' }}>
        You can help improve the inventory by sharing data, assisting with field
        reconnaissance to evaluate the impact of aquatic barriers, joining an{' '}
        <OutboundLink to={`${naccURL}/teams/`}>
          Aquatic Connectivity Team
        </OutboundLink>
        , or even by reporting issues with the inventory data in this tool.
        <br />
        <br />
        <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn more
        about how you can help improve this barrier inventory and tool.
        <br />
        <br />
        If you are not able to get what you need from this tool or if you need
        to report an issue, please&nbsp;
        <a href="mailto:kat@southeastaquatics.net">let us know</a>!
      </Paragraph>
    </Box>
  </Box>
)

export default GetInvolvedSection
