import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { formatNumber } from 'util/format'

import { Bold, List, ListItem } from './elements'

const Network = ({
  barrierType,
  hasnetwork,
  totalupstreammiles,
  freedownstreammiles,
  freeupstreammiles,
  totaldownstreammiles,
  landcover,
  sizeclasses,
  excluded,
}) => {
  const typeLabel = barrierType === 'dams' ? 'dam' : 'road-related barrier'

  const header = (
    <View style={{ marginBottom: 4 }}>
      <Bold
        style={{
          fontSize: 14,
        }}
      >
        Functional network information
      </Bold>
    </View>
  )

  if (excluded) {
    return (
      <View>
        {header}
        <Text>
          This {typeLabel} was excluded from the connectivity analysis based on
          field reconnaissance or manual review of aerial imagery.
        </Text>
      </View>
    )
  }

  if (!hasnetwork) {
    return (
      <View>
        {header}
        <Text>
          This {typeLabel} is off-network and has no functional network
          information.
          {'\n\n'}
        </Text>
        <Text style={{ color: '#7f8a93' }}>
          Not all {barrierType} could be correctly snapped to the aquatic
          network for analysis. Please contact us to report an error or for
          assistance interpreting these results.
        </Text>
      </View>
    )
  }

  return (
    <List title="Functional network information">
      <ListItem>
        <Text>
          <Bold>
            {formatNumber(Math.min(totalupstreammiles, freedownstreammiles))}{' '}
            miles
          </Bold>{' '}
          could be gained by removing this {typeLabel}.
        </Text>

        <ListItem style={{ marginTop: 4 }}>
          <Text>
            {formatNumber(freeupstreammiles)} free-flowing miles upstream
          </Text>

          <ListItem style={{ marginTop: 4 }}>
            <Text>
              <Bold>{formatNumber(totalupstreammiles)} total miles</Bold> in the
              upstream network
            </Text>
          </ListItem>
        </ListItem>

        <ListItem>
          <Text>
            <Bold>{formatNumber(freedownstreammiles)} free-flowing miles</Bold>{' '}
            in the downstream network
          </Text>

          <ListItem style={{ marginTop: 4 }}>
            <Text>
              {formatNumber(totaldownstreammiles)} total miles in the downstream
              network
            </Text>
          </ListItem>
        </ListItem>
      </ListItem>
      <ListItem>
        <Text>
          <Bold>{sizeclasses}</Bold> river size{' '}
          {sizeclasses === 1 ? 'class' : 'classes'} could be gained by removing
          this {typeLabel}
        </Text>
      </ListItem>
      <ListItem>
        <Text>
          <Bold>{formatNumber(landcover, 0)}%</Bold> of the upstream floodplain
          is composed of natural landcover
        </Text>
      </ListItem>
    </List>
  )
}

Network.propTypes = {
  barrierType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  freeupstreammiles: PropTypes.number,
  totalupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  totaldownstreammiles: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
}

Network.defaultProps = {
  excluded: false,
  freeupstreammiles: null,
  totalupstreammiles: null,
  freedownstreammiles: null,
  totaldownstreammiles: null,
  landcover: null,
  sizeclasses: null,
}

export default Network
