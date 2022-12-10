import React from 'react'
import PropTypes from 'prop-types'

import { Box, Flex, Text } from 'theme-ui'

import { STATES } from 'config'
import { formatNumber } from 'util/format'

const Header = ({ name, county, state, lat, lon }) => (
  <Flex sx={{ alignItems: 'flex-end', mb: ' 0.5rem', lineHeight: 1.2 }}>
    <Box sx={{ flex: '1 1 auto' }}>
      <Text sx={{ fontSize: '2rem', fontWeight: 'bold' }}>{name}</Text>
      <Flex sx={{ justifyContent: 'space-between', mt: '0.5rem' }}>
        <Text sx={{ flex: '1 1 auto', color: 'grey.8' }}>
          {county} County, {STATES[state]}
        </Text>
        <Text sx={{ flex: '0 0 auto', color: 'grey.8' }}>
          Located at {formatNumber(lat, 5)}
          &deg; N / {formatNumber(lon, 5)}
          &deg; E
        </Text>
      </Flex>
    </Box>
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
