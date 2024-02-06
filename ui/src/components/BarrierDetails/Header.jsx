import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Heading, Text } from 'theme-ui'
import { FileDownload, Water } from '@emotion-icons/fa-solid'

import { STATES } from 'config'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

const Header = ({
  barrierType,
  networkType,
  sarpid,
  name,
  county,
  state,
  lat,
  lon,
  removed,
  yearremoved,
  onClose,
}) => (
  <Box
    sx={{
      py: '0.5rem',
      px: '0.5rem',
      borderBottom: '4px solid',
      borderBottomColor: 'blue.2',
    }}
  >
    <Flex
      sx={{
        flex: '0 0 auto',
        justifyContent: 'space-between',
      }}
    >
      <Box sx={{ flex: '1 1 auto', mb: '0.5rem' }}>
        <Heading as="h3" sx={{ m: 0, fontSize: '1.25rem' }}>
          {name}
        </Heading>
        {removed ? (
          <Flex
            sx={{
              alignItems: 'center',
              gap: '0.5rem',
              mt: '0.25rem',
            }}
          >
            <Box sx={{ color: 'blue.8' }}>
              <Water size="1em" />
            </Box>
            {yearremoved !== null && yearremoved !== 0 ? (
              <Text sx={{ fontWeight: 'bold' }}>
                Removed / mitigated in {yearremoved}
              </Text>
            ) : (
              <Flex sx={{ alignItems: 'baseline', gap: '0.25rem' }}>
                <Text sx={{ fontWeight: 'bold' }}>Removed / mitigated</Text>
                <Text sx={{ fontSize: 0 }}>(year unknown)</Text>
              </Flex>
            )}
          </Flex>
        ) : null}
      </Box>
      <Button variant="close" onClick={onClose}>
        &#10006;
      </Button>
    </Flex>

    <Flex sx={{ color: 'grey.8', fontSize: 1, lineHeight: 1.1 }}>
      <Text sx={{ flex: '1 1 auto', mr: '1rem' }}>
        {!isEmptyString(state) ? `${county} County, ${STATES[state]}` : ''}
      </Text>

      <Text sx={{ flex: '0 0 auto', textAlign: 'right' }}>
        {formatNumber(lat, 3)}
        &deg; N, {formatNumber(lon, 3)}
        &deg; E
      </Text>
    </Flex>

    {/* Only show report for dams / small barriers */}
    {barrierType === 'dams' || barrierType === 'small_barriers' ? (
      <Box sx={{ lineHeight: 1, mt: '1.5rem' }}>
        <a
          href={`/report/${
            networkType === 'small_barriers' ? 'combined_barriers' : networkType
          }/${sarpid}`}
          target="_blank"
          rel="noreferrer"
          style={{ display: 'inline-block' }}
        >
          <Flex
            sx={{
              alignItems: 'baseline',
            }}
          >
            <Box sx={{ flex: '0 0 auto', color: 'link', mr: '0.25rem' }}>
              <FileDownload size="1em" />
            </Box>
            <Text>Create PDF report</Text>
          </Flex>
        </a>
      </Box>
    ) : null}
  </Box>
)

Header.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  name: PropTypes.string,
  county: PropTypes.string,
  state: PropTypes.string,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
  onClose: PropTypes.func.isRequired,
}

Header.defaultProps = {
  name: '',
  county: '',
  state: '',
  removed: false,
  yearremoved: null,
}

export default Header
