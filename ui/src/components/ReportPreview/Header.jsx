import React from 'react'
import PropTypes from 'prop-types'
import { Fish, Water } from '@emotion-icons/fa-solid'
import { Box, Flex, Text } from 'theme-ui'

import { barrierTypeLabelSingular, STATES } from 'config'
import { formatNumber } from 'util/format'

const Header = ({
  barrierType,
  name,
  county,
  state,
  lat,
  lon,
  removed,
  yearremoved,
  ispriority,
  lowheaddam,
  diversion,
  invasive,
  estimated,
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]
  const isLowheadDam = lowheaddam === 1 || lowheaddam === 2
  const isDiversion = diversion !== null && diversion >= 1

  return (
    <Flex sx={{ alignItems: 'flex-end', mb: ' 0.5rem', lineHeight: 1.2 }}>
      <Box sx={{ flex: '1 1 auto' }}>
        <Text sx={{ fontSize: '2rem', fontWeight: 'bold' }}>{name}</Text>
        {removed ? (
          <Flex
            sx={{
              alignItems: 'center',
              gap: '0.5rem',
              mt: '0.25rem',
              mb: '1rem',
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

        {ispriority && !removed ? (
          <Flex
            sx={{
              alignItems: 'center',
              gap: '0.5rem',
              mt: '0.25rem',
              mb: '1rem',
            }}
          >
            <Box sx={{ color: 'blue.8' }}>
              <Fish size="1.5em" style={{ transform: 'rotate(180deg)' }} />
            </Box>
            <Text sx={{ fontWeight: 'bold' }}>
              Identified as a priority by resource managers
            </Text>
          </Flex>
        ) : null}

        <Box sx={{ color: 'grey.8' }}>
          Barrier type:{' '}
          {isLowheadDam ? (
            <>
              {lowheaddam === 2 ? 'likely ' : null}
              lowhead dam
            </>
          ) : null}
          {isDiversion ? (
            <>
              {isLowheadDam ? ',' : null} {diversion === 2 ? 'likely ' : null}{' '}
              water diversion
            </>
          ) : null}
          {estimated ? 'estimated ' : ''}
          {!(isLowheadDam || isDiversion) ? barrierTypeLabel : null}
          {invasive ? <>, invasive species barrier</> : null}
        </Box>

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
}

Header.propTypes = {
  barrierType: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  county: PropTypes.string.isRequired,
  state: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
  ispriority: PropTypes.bool,
  lowheaddam: PropTypes.number,
  diversion: PropTypes.number,
  invasive: PropTypes.bool,
  estimated: PropTypes.bool,
}

Header.defaultProps = {
  removed: false,
  yearremoved: null,
  ispriority: false,
  lowheaddam: 0,
  diversion: 0,
  invasive: false,
  estimated: false,
}

export default Header
