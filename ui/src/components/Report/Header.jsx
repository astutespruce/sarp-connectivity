import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { STATES } from 'config'
import { formatNumber } from 'util/format'
import { Flex } from './elements'

const Header = ({ name, county, state, lat, lon }) => (
  <View style={{ marginBottom: 4 }}>
    <Text
      style={{ fontFamily: 'Helvetica-Bold', fontSize: 24, lineHeight: 1.2 }}
    >
      {name}
    </Text>
    <Flex
      style={{
        justifyContent: 'space-beteween',
        marginTop: 12,
      }}
    >
      <Text
        style={{
          flex: '1 1 auto',
          fontSize: 12,
          color: '#5f6e78',
        }}
      >
        {county} County, {STATES[state]}
      </Text>
      <Text style={{ flex: '0 0 210', textAlign: 'right', color: '#5f6e78' }}>
        Located at {formatNumber(lat, 5)}
        &deg; N / {formatNumber(lon, 5)}
        &deg; E
      </Text>
    </Flex>
  </View>
)

Header.propTypes = {
  name: PropTypes.string.isRequired,
  county: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
}

export default Header
