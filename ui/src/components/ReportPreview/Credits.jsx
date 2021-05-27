import React from 'react'
import { Box, Flex, Image } from 'theme-ui'

import SARPLogoImage from 'images/sarp_logo.png'

const Credits = () => (
  <Box>
    <Flex sx={{ mt: '0.5rem', fontSize: 1 }}>
      <Box sx={{ flex: '1 1 auto' }}>
        This report was created using the{' '}
        <a href="https://connectivity.sarpdata.com/">
          Southeast Aquatic Barrier Prioritization Tool
        </a>
        , a project of the{' '}
        <a href="https://southeastaquatics.net/">
          Southeast Aquatic Resources Partnership
        </a>
        .
        <br />
        <br />
        This project was supported in part by grants from the&nbsp;
        <a href="https://www.fws.gov/fisheries/fish-passage.html">
          U.S. Fish and Wildlife Service Fish Passage Program
        </a>
        , the&nbsp;
        <a href="https://gcpolcc.org/">
          Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
        </a>
        , and the&nbsp;
        <a href="https://myfwc.com/conservation/special-initiatives/fwli/grant/">
          Florida State Wildlife Grants Program
        </a>
        .
      </Box>
      <Box sx={{ flex: '0 0 auto', ml: '2rem' }}>
        <Image src={SARPLogoImage} sx={{ width: '100pt' }} />
      </Box>
    </Flex>
  </Box>
)

export default Credits
