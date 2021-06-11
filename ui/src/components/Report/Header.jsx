import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { formatNumber } from 'util/format'
import { Flex } from './elements'

const Header = ({ name, county, state, lat, lon }) => (
  <Flex
    style={{
      marginBottom: 6,
      alignItems: 'flex-end',
      justifyContent: 'space-between',
    }}
  >
    <View style={{ flex: '1 1 auto', marginRight: 24 }}>
      <Text
        style={{ fontFamily: 'Helvetica-Bold', fontSize: 24, lineHeight: 1.2 }}
      >
        {name}
      </Text>
      <Text
        style={{
          fontStyle: 'italic',
          fontFamily: 'Helvetica-Oblique',
          fontSize: 12,
        }}
      >
        {county} County, {state}
      </Text>
    </View>

    <View sx={{ flex: '0 0 80' }}>
      <Text>
        {`${formatNumber(lat, 3)}° N`}
        {'\n'}
        {`${formatNumber(lon, 3)}° E`}
      </Text>
    </View>
  </Flex>
)

Header.propTypes = {
  name: PropTypes.string.isRequired,
  county: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
}

export default Header
