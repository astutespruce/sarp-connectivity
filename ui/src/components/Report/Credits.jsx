import React from 'react'
import { Image, Text } from '@react-pdf/renderer'

import SARPLogoImage from 'images/sarp_logo.png'
import { Flex, Link } from './elements'

const Credits = (props) => (
  <Flex {...props} wrap={false}>
    <Text style={{ flex: '1 1 auto', marginRight: 36, fontSize: 10 }}>
      This report was created using the{' '}
      <Link href="https://connectivity.sarpdata.com/">
        <Text>Aquatic Barrier Prioritization Tool</Text>
      </Link>
      , a project of the{' '}
      <Link href="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
        <Text>Southeast Aquatic Resources Partnership</Text>
      </Link>
      .{'\n\n'}
      This project was supported in part by grants from the{'\n'}
      <Link href="https://www.fws.gov/fisheries/fish-passage.html">
        <Text>U.S. Fish and Wildlife Service Fish Passage Program</Text>
      </Link>
      , the&nbsp;
      <Link href="https://gcpolcc.org/">
        <Text>
          Gulf Coastal Plains and Ozarks Landscape Conservation Cooperative
        </Text>
      </Link>
      , and the&nbsp;
      <Link href="https://myfwc.com/conservation/special-initiatives/fwli/grant/">
        <Text>Florida State Wildlife Grants Program</Text>
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
