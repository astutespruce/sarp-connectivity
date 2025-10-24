import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Image } from 'theme-ui'

import SARPLogoImage from 'images/sarp_logo.png'

const Credits = ({ sx }) => (
  <Box sx={sx}>
    <Flex sx={{ mt: '0.5rem', fontSize: 1 }}>
      <Box sx={{ flex: '1 1 auto' }}>
        This report was created using the{' '}
        <a href="https://tool.aquaticbarriers.org/">
          National Aquatic Barrier Inventory & Prioritization Tool
        </a>
        , a project of the{' '}
        <a href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
          Southeast Aquatic Resources Partnership
        </a>
        .
        <br />
        <br />
        This project was supported in part by grants from the{' '}
        <a href="https://www.fws.gov/fisheries/fish-passage.html">
          {' '}
          U.S. Fish and Wildlife Service Fish Passage Program
        </a>
        , <a href="https://www.americanrivers.org/">American Rivers</a>, the{' '}
        <a href="https://www.fs.usda.gov/">
          U.S. Department of Agriculture, Forest Service
        </a>
        , the{' '}
        <a href="https://www.nfwf.org/">
          National Fish and Wildlife Foundation
        </a>
        , <a href="https://www.nature.org/">The Nature Conservancy</a>,{' '}
        <a href="https://www.tu.org/">Trout Unlimited</a>, the{' '}
        <a href="https://gcpolcc.org/">
          Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
        </a>
        , and the{' '}
        <a href="https://myfwc.com/conservation/special-initiatives/swap/grant/">
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

Credits.propTypes = {
  sx: PropTypes.object,
}

Credits.defaultProps = {
  sx: null,
}

export default Credits
