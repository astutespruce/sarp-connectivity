import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { formatNumber } from 'util/format'

import { Bold, List, ListItem } from './elements'

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
  <List title="Functional network information">
    {hasnetwork ? (
      <>
        <ListItem>
          <Text>
            <Bold>
              {formatNumber(Math.min(totalupstreammiles, freedownstreammiles))}{' '}
              miles
            </Bold>{' '}
            could be gained by removing this barrier.
          </Text>

          <ListItem style={{ marginTop: 4 }}>
            <Text>
              {formatNumber(freeupstreammiles)} free-flowing miles upstream
            </Text>

            <ListItem style={{ marginTop: 4 }}>
              <Text>
                <Bold>{formatNumber(totalupstreammiles)} total miles</Bold> in
                the upstream network
              </Text>
            </ListItem>
          </ListItem>

          <ListItem>
            <Text>
              <Bold>
                {formatNumber(freedownstreammiles)} free-flowing miles
              </Bold>{' '}
              in the downstream network
            </Text>

            <ListItem style={{ marginTop: 4 }}>
              <Text>
                {formatNumber(totaldownstreammiles)} total miles in the
                downstream network
              </Text>
            </ListItem>
          </ListItem>
        </ListItem>
        <ListItem>
          <Text>
            <Bold>{sizeclasses}</Bold> river size{' '}
            {sizeclasses === 1 ? 'class' : 'classes'} could be gained by
            removing this barrier
          </Text>
        </ListItem>
        <ListItem>
          <Text>
            <Bold>{formatNumber(landcover, 0)}%</Bold> of the upstream
            floodplain is composed of natural landcover
          </Text>
        </ListItem>
        <ListItem>
          <Text>
            The upstream network has <Bold>{SINUOSITY[sinuosityclass]}</Bold>{' '}
            sinuosity
          </Text>
        </ListItem>
      </>
    ) : (
      <>
        {excluded ? (
          <ListItem>
            <Text>
              This dam was excluded from the connectivity analysis based on
              field reconnaissance or manual review of aerial imagery.
            </Text>
          </ListItem>
        ) : (
          <>
            <ListItem>
              <Text>
                This dam is off-network and has no functional network
                information.
                <Text style={{ color: '#7f8a93' }}>
                  Not all dams could be correctly snapped to the aquatic network
                  for analysis. Please contact us to report an error or for
                  assistance interpreting these results.
                </Text>
              </Text>
            </ListItem>
          </>
        )}
      </>
    )}
  </List>
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
