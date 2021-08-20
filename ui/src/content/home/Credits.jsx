import React from 'react'
import { Box, Divider, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/Link'

const Credits = () => (
  <Box variant="boxes.section" sx={{ mb: '4rem' }}>
    <Divider />

    <Box>
      <Paragraph>
        This application was created by{' '}
        <a href="mailto:bcward@consbio.org">Brendan C. Ward</a> (
        <OutboundLink to="https://astutespruce.com/">
          Astute Spruce, LLC
        </OutboundLink>
        ) in partnership with{' '}
        <a href="mailto:jessica@southeastaquatics.net">Jessica Graham</a> and{' '}
        <a href="mailto:kat@southeastaquatics.net">Kat Hoenke</a> at the{' '}
        <OutboundLink to="https://southeastaquatics.net/">
          Southeast Aquatic Resources Partnership
        </OutboundLink>
        . CBI provides science and software development to support the
        conservation of biodiversity.
      </Paragraph>
    </Box>
    <Paragraph>
      <br />
      This project was supported in part by grants from the&nbsp;
      <OutboundLink to="https://www.fws.gov/fisheries/fish-passage.html">
        U.S. Fish and Wildlife Service Fish Passage Program
      </OutboundLink>
      , the&nbsp;
      <OutboundLink to="https://gcpolcc.org/">
        Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
      </OutboundLink>
      , and the&nbsp;
      <OutboundLink to="https://myfwc.com/conservation/special-initiatives/fwli/grant/">
        Florida State Wildlife Grants Program
      </OutboundLink>
      .
    </Paragraph>
  </Box>
)

export default Credits
