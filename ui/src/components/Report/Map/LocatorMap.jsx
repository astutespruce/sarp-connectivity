import React from 'react'
import PropTypes from 'prop-types'
import { Image, View } from '@react-pdf/renderer'

const LocatorMap = ({ map }) => (
  <View
    style={{
      flex: '0 0 144',
      border: '1 solid #AAA',
      width: 144,
      height: 144,
      marginRight: 12,
    }}
  >
    <Image src={map} style={{ width: 142, height: 142 }} />
  </View>
)

LocatorMap.propTypes = {
  map: PropTypes.string.isRequired,
}

export default LocatorMap
