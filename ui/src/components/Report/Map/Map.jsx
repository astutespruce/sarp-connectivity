import React from 'react'
import PropTypes from 'prop-types'
import { Image, View, Text } from '@react-pdf/renderer'

import MapboxLogo from 'images/mapbox-logo.png'

import { Flex } from '../elements'

// NOTE: scale width is adjusted from pixels to points
// pt = 0.75*px

const Map = ({
  map,
  attribution,
  scale: { width: scaleWidth, label: scaleLabel },
}) => (
  <View style={{ marginBottom: 24 }}>
    <View
      style={{
        border: '1 solid #AAA',
        position: 'relative',
        width: 540,
        height: 396,
        zIndex: 0,
      }}
    >
      <Image
        src={map}
        style={{
          position: 'relative',
          top: 0,
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 2, // WARNING: due to a bug in react-pdf, zIndex is evaluated incorrectly
          width: 538,
          height: 396,
        }}
      />

      <View
        style={{
          width: scaleWidth * 0.75,
          height: 16,
          backgroundColor: 'rgba(255,255,255, 0.75)',
          position: 'absolute',
          zIndex: 1,
          right: 10,
          bottom: 10,
          border: '2px solid #333',
          borderTopWidth: 0,
          paddingHorizontal: 5,
          paddingVertical: 4,
          overflow: 'hidden',
        }}
      >
        <Text
          style={{
            fontSize: 7,
            color: '#333',
            position: 'absolute',
            top: 4,
            left: 4,
            zIndex: 2,
          }}
        >
          {scaleLabel}
        </Text>
      </View>
    </View>
    <Flex style={{ alignItems: 'center', marginTop: 4 }}>
      <View style={{ flex: '0 0 50', height: 12, marginRight: 12 }}>
        <Image src={MapboxLogo} style={{ height: 11, width: 50 }} />
      </View>
      <Text style={{ fontSize: 8, color: '#7f8a93', flex: '1 1 auto' }}>
        Basemap credits: {attribution}
      </Text>
    </Flex>
  </View>
)

Map.propTypes = {
  map: PropTypes.string.isRequired,
  attribution: PropTypes.string.isRequired,
  scale: PropTypes.shape({
    width: PropTypes.number.isRequired,
    label: PropTypes.string.isRequired,
  }).isRequired,
}

export default Map
