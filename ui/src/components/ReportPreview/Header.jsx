import React from 'react'
import PropTypes from 'prop-types'

import { Box, Flex, Text } from 'theme-ui'

import { formatNumber } from 'util/format'

const Header = ({ barrierType, name, county, state, lat, lon }) => (
  <Flex sx={{ alignItems: 'flex-end', mb: ' 0.5rem', lineHeight: 1.2 }}>
    <Box sx={{ flex: '1 1 auto' }}>
      <Text sx={{ fontSize: '2rem', fontWeight: 'bold' }}>{name}</Text>
      <Flex sx={{ justifyContent: 'space-between', mt: '0.5rem' }}>
        <Text sx={{ flex: '1 1 auto' }}>
          {barrierType === 'dams' ? 'Dam' : 'Road-related barrier'} at{' '}
          {formatNumber(lat, 3)}
          &deg; N / {formatNumber(lon, 3)}
          &deg; E
        </Text>
        <Text sx={{ flex: '0 0 auto', fontStyle: 'italic' }}>
          {county} County, {state}
        </Text>
      </Flex>
    </Box>
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
