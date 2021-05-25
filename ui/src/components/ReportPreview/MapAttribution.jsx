import React from 'react'
import PropTypes from 'prop-types'
import { Flex, Image, Text } from 'theme-ui'

import MapboxLogo from 'images/mapbox-logo.png'

const MapAttribution = ({ attribution }) => (
  <Flex sx={{ alignItems: 'center', mt: '0.25rem', lineHeight: 1.1 }}>
    <Image
      src={MapboxLogo}
      sx={{ height: '16px', mr: '1rem', flex: '0 0 auto' }}
    />
    <Text sx={{ fontSize: '10px', color: 'grey.7', flex: '1 1 auto' }}>
      Basemap credits: {attribution}
    </Text>
  </Flex>
)

MapAttribution.propTypes = {
  attribution: PropTypes.string.isRequired,
}

export default MapAttribution
