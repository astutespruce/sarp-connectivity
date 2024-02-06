import React from 'react'
import PropTypes from 'prop-types'
import { Water } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

import { STATES } from 'config'
import { formatNumber } from 'util/format'

const Header = ({ name, county, state, lat, lon, removed, yearremoved }) => (
  <Flex sx={{ alignItems: 'flex-end', mb: ' 0.5rem', lineHeight: 1.2 }}>
    <Box sx={{ flex: '1 1 auto' }}>
      <Text sx={{ fontSize: '2rem', fontWeight: 'bold' }}>{name}</Text>
      {removed ? (
        <Flex
          sx={{
            alignItems: 'center',
            gap: '0.5rem',
            mt: '0.25rem',
          }}
        >
          <Box sx={{ color: 'blue.8', mb: '2px' }}>
            <Water size="1em" />
          </Box>

          <Text sx={{ fontWeight: 'bold' }}>
            Removed / mitigated{' '}
            {yearremoved !== null && yearremoved !== 0
              ? `in ${yearremoved}`
              : `(year unknown)`}
          </Text>
        </Flex>
      ) : null}
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
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
}

Header.defaultProps = {
  removed: false,
  yearremoved: null,
}

export default Header
