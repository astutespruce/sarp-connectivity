import React from 'react'
import PropTypes from 'prop-types'

import { Box, Flex, Text } from 'theme-ui'

import { formatNumber } from 'util/format'

const Header = ({
  name,
  county,
  state,

  lat,
  lon,
}) => (
  <Flex sx={{ alignItems: 'flex-end', mb: ' 0.5rem', lineHeight: 1.2 }}>
    <Box sx={{ flex: '1 1 auto', mr: '2rem' }}>
      <Text sx={{ fontSize: '2rem', fontWeight: 'bold' }}>{name}</Text>
      <Text sx={{ fontStyle: 'italic' }}>
        {county} County, {state}
      </Text>
    </Box>
    <Box sx={{ flex: '0 0 auto', textAlign: 'right' }}>
      {formatNumber(lat, 3)}
      &deg; N
      <br />
      {formatNumber(lon, 3)}
      &deg; E
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
