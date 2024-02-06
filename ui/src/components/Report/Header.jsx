import React from 'react'
import PropTypes from 'prop-types'
import { Text, View, Svg, Path } from '@react-pdf/renderer'

import { STATES } from 'config'
import { formatNumber } from 'util/format'
import { Flex } from './elements'

const Header = ({ name, county, state, lat, lon, removed, yearremoved }) => (
  <View style={{ marginBottom: 4 }}>
    <Text
      style={{ fontFamily: 'Helvetica-Bold', fontSize: 24, lineHeight: 1.2 }}
    >
      {name}
    </Text>

    {removed ? (
      <Flex
        style={{
          marginTop: '2pt',
          lineHeight: 1,
        }}
      >
        {/* Water icon: Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc. */}
        <div style={{ marginRight: '4pt' }}>
          <Svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 576 512"
            style={{ width: '12pt', height: '12pt' }}
          >
            <Path
              d="M562.1 383.9c-21.5-2.4-42.1-10.5-57.9-22.9-14.1-11.1-34.2-11.3-48.2 0-37.9 30.4-107.2 30.4-145.7-1.5-13.5-11.2-33-9.1-46.7 1.8-38 30.1-106.9 30-145.2-1.7-13.5-11.2-33.3-8.9-47.1 2-15.5 12.2-36 20.1-57.7 22.4-7.9 .8-13.6 7.8-13.6 15.7v32.2c0 9.1 7.6 16.8 16.7 16 28.8-2.5 56.1-11.4 79.4-25.9 56.5 34.6 137 34.1 192 0 56.5 34.6 137 34.1 192 0 23.3 14.2 50.9 23.3 79.1 25.8 9.1 .8 16.7-6.9 16.7-16v-31.6c.1-8-5.7-15.4-13.8-16.3zm0-144c-21.5-2.4-42.1-10.5-57.9-22.9-14.1-11.1-34.2-11.3-48.2 0-37.9 30.4-107.2 30.4-145.7-1.5-13.5-11.2-33-9.1-46.7 1.8-38 30.1-106.9 30-145.2-1.7-13.5-11.2-33.3-8.9-47.1 2-15.5 12.2-36 20.1-57.7 22.4-7.9 .8-13.6 7.8-13.6 15.7v32.2c0 9.1 7.6 16.8 16.7 16 28.8-2.5 56.1-11.4 79.4-25.9 56.5 34.6 137 34.1 192 0 56.5 34.6 137 34.1 192 0 23.3 14.2 50.9 23.3 79.1 25.8 9.1 .8 16.7-6.9 16.7-16v-31.6c.1-8-5.7-15.4-13.8-16.3zm0-144C540.6 93.4 520 85.4 504.2 73 490.1 61.9 470 61.7 456 73c-37.9 30.4-107.2 30.4-145.7-1.5-13.5-11.2-33-9.1-46.7 1.8-38 30.1-106.9 30-145.2-1.7-13.5-11.2-33.3-8.9-47.1 2-15.5 12.2-36 20.1-57.7 22.4-7.9 .8-13.6 7.8-13.6 15.7v32.2c0 9.1 7.6 16.8 16.7 16 28.8-2.5 56.1-11.4 79.4-25.9 56.5 34.6 137 34.1 192 0 56.5 34.6 137 34.1 192 0 23.3 14.2 50.9 23.3 79.1 25.8 9.1 .8 16.7-6.9 16.7-16v-31.6c.1-8-5.7-15.4-13.8-16.3z"
              fill="#1f5f8b"
            />
          </Svg>
        </div>

        <Text style={{ fontFamily: 'Helvetica-Bold' }}>
          Removed / mitigated{' '}
          {yearremoved !== null && yearremoved !== 0
            ? `in ${yearremoved}`
            : `(year unknown)`}
        </Text>
      </Flex>
    ) : null}

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
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
}

Header.defaultProps = {
  removed: false,
  yearremoved: null,
}

export default Header
