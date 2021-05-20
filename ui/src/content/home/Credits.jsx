import React from 'react'
import { Box, Divider, Grid, Image, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import CBILogoImage from 'images/cbi_logo.png'
import AstuteSpruceLogoImage from 'images/Astute_Spruce_logo.png'

const Credits = () => (
  <Box variant="boxes.section" sx={{ mb: '4rem' }}>
    <Divider />

    <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '2rem' }}>
      <Box>
        <Paragraph>
          This application was created by{' '}
          <a href="mailto:bcward@consbio.org">Brendan C. Ward</a> at the{' '}
          <OutboundLink to="https://consbio.org">
            Conservation Biology Institute
          </OutboundLink>{' '}
          (CBI), now with{' '}
          <OutboundLink to="https://astutespruce.com/">
            Astute Spruce, LLC,
          </OutboundLink>{' '}
          in partnership with{' '}
          <a href="mailto:jessica@southeastaquatics.net">Jessica Graham</a> and{' '}
          <a href="mailto:kat@southeastaquatics.net">Kat Hoenke</a> at the{' '}
          <OutboundLink to="https://southeastaquatics.net/">
            Southeast Aquatic Resources Partnership
          </OutboundLink>
          . CBI provides science and software development to support the
          conservation of biodiversity.
        </Paragraph>
      </Box>
      <Box>
        <OutboundLink to="https://consbio.org">
          <Image src={CBILogoImage} sx={{ maxWidth: '300px', mb: '1rem' }} />
        </OutboundLink>

        <OutboundLink to="https://astutespruce.com/">
          <Image src={AstuteSpruceLogoImage} sx={{ maxWidth: '300px' }} />
        </OutboundLink>
      </Box>
    </Grid>
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
