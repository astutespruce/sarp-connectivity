/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'

import { HelpText } from 'components/Text'
import { formatNumber } from 'util/format'
import styled from 'style'

const List = styled.ul`
  margin-top: 1rem;
`

const Dams = ({ dams, on_network_dams, miles }) => {
  const offNetworkDams = dams - on_network_dams

  if (dams === 0) {
    return <HelpText>This area does not yet have any inventoried dams</HelpText>
  }

  return (
    <>
      This area contains:
      <List>
        <li>
          <b>{formatNumber(dams, 0)}</b> inventoried {dams > 1 ? 'dams' : 'dam'}
        </li>
        <li>
          <b>{formatNumber(on_network_dams, 0)}</b>{' '}
          {on_network_dams > 1 ? 'dams' : 'dam'} that{' '}
          {on_network_dams > 1 ? 'were ' : 'was '} analyzed for impacts to
          aquatic connectivity in this tool
        </li>
        <li>
          <b>{formatNumber(miles, 2)}</b> miles of connected rivers and streams
        </li>
      </List>
      <HelpText>
        <br />
        Note: These statistics are based on <i>inventoried</i> dams. Because the
        inventory is incomplete in many areas, areas with a high number of dams
        may simply represent areas that have a more complete inventory.
        {offNetworkDams > 0 ? (
          <>
            <br />
            <br />
            {formatNumber(offNetworkDams, 0)}{' '}
            {offNetworkDams > 1 ? 'dams' : 'dam'} were not analyzed because they
            were not on the aquatic network or could not be correctly located on
            the network.
          </>
        ) : null}
      </HelpText>
    </>
  )
}

Dams.propTypes = {
  dams: PropTypes.number,
  on_network_dams: PropTypes.number,
  miles: PropTypes.number,
}

Dams.defaultProps = {
  dams: 0,
  on_network_dams: 0,
  miles: 0,
}

export default Dams
