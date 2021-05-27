import React from 'react'
import { Image, Text } from '@react-pdf/renderer'

import SARPLogoImage from 'images/sarp_logo.png'
import { Flex, Link } from './elements'

const Credits = () => (
  <Flex>
    <Text style={{ flex: '1 1 auto', marginRight: 36, fontSize: 10 }}>
      This report was created using the{' '}
      <Link href="https://connectivity.sarpdata.com/">
        Southeast Aquatic Barrier Prioritization Tool
      </Link>
      , a project of the{' '}
      <Link href="https://southeastaquatics.net/">
        Southeast Aquatic Resources Partnership
      </Link>
      .{'\n\n'}
      This project was supported in part by grants from the&nbsp;
      <Link href="https://www.fws.gov/fisheries/fish-passage.html">
        U.S. Fish and Wildlife Service Fish Passage Program
      </Link>
      , the&nbsp;
      <Link href="https://gcpolcc.org/">
        Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
      </Link>
      , and the&nbsp;
      <Link href="https://myfwc.com/conservation/special-initiatives/fwli/grant/">
        Florida State Wildlife Grants Program
      </Link>
      .
    </Text>

    <Image
      src={SARPLogoImage}
      style={{ width: 100, height: 50, flex: '0 0 100' }}
    />
  </Flex>
)

export default Credits
