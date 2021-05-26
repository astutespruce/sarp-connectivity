import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph, Text } from 'theme-ui'

import { formatNumber } from 'util/format'
import { SINUOSITY } from '../../../config/constants'

const Network = ({
  hasnetwork,
  totalupstreammiles,
  freedownstreammiles,
  freeupstreammiles,
  totaldownstreammiles,
  sinuosityclass,
  landcover,
  sizeclasses,
  excluded,
}) => (
  <Box>
    <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
      Functional network information
    </Text>
    <Box as="ul" sx={{ mt: '0.5rem' }}>
      {hasnetwork ? (
        <>
          <li>
            <b>
              {formatNumber(Math.min(totalupstreammiles, freedownstreammiles))}{' '}
              miles
            </b>{' '}
            could be gained by removing this barrier.
            <Box as="ul" sx={{ mt: '0.5rem' }}>
              <li>
                {formatNumber(freeupstreammiles)} free-flowing miles upstream
                <ul>
                  <li>
                    <b>{formatNumber(totalupstreammiles)} total miles</b> in the
                    upstream network
                  </li>
                </ul>
              </li>

              <li>
                <b>{formatNumber(freedownstreammiles)} free-flowing miles</b> in
                the downstream network
                <ul>
                  <li>
                    {formatNumber(totaldownstreammiles)} total miles in the
                    downstream network
                  </li>
                </ul>
              </li>
            </Box>
          </li>
          <li>
            <b>{sizeclasses}</b> river size{' '}
            {sizeclasses === 1 ? 'class' : 'classes'} could be gained by
            removing this barrier
          </li>
          <li>
            <b>{formatNumber(landcover, 0)}%</b> of the upstream floodplain is
            composed of natural landcover
          </li>
          <li>
            The upstream network has <b>{SINUOSITY[sinuosityclass]}</b>{' '}
            sinuosity
          </li>
        </>
      ) : (
        <>
          {excluded ? (
            <li>
              This dam was excluded from the connectivity analysis based on
              field reconnaissance or manual review of aerial imagery.
            </li>
          ) : (
            <>
              <li>
                This dam is off-network and has no functional network
                information.
              </li>
              <Paragraph variant="help" sx={{ mt: '1rem' }}>
                Not all dams could be correctly snapped to the aquatic network
                for analysis. Please contact us to report an error or for
                assistance interpreting these results.
              </Paragraph>
            </>
          )}
        </>
      )}
    </Box>
  </Box>
)

Network.propTypes = {
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  freeupstreammiles: PropTypes.number,
  totalupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  totaldownstreammiles: PropTypes.number,
  sinuosityclass: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
}

Network.defaultProps = {
  excluded: false,
  freeupstreammiles: null,
  totalupstreammiles: null,
  freedownstreammiles: null,
  totaldownstreammiles: null,
  sinuosityclass: null,
  landcover: null,
  sizeclasses: null,
}

export default Network
