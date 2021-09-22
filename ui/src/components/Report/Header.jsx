import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { formatNumber } from 'util/format'
import { Flex } from './elements'

const Header = ({ barrierType, name, county, state, lat, lon }) => (
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
      <Flex style={{ justifyContent: 'space-beteween', marginTop: 12 }}>
        <Text style={{ flex: '1 1 auto' }}>
          {barrierType === 'dams' ? 'Dam' : 'Road-related barrier'} at{' '}
          {formatNumber(lat, 3)}
          &deg; N / {formatNumber(lon, 3)}
          &deg; E
        </Text>
        <Text
          style={{
            flex: '0 0 200',
            fontStyle: 'italic',
            fontFamily: 'Helvetica-Oblique',
            fontSize: 12,
            textAlign: 'right',
          }}
        >
          {county} County, {state}
        </Text>
      </Flex>
    </View>
  </Flex>
)

Header.propTypes = {
  barrierType: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  county: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
}

export default Header
