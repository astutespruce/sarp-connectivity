/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText } from 'components/Text'
import { Box, Flex } from 'components/Grid'
import { formatNumber } from 'util/format'
import { Downloader } from 'components/Download'
import styled, { themeGet } from 'style'

const List = styled.ul`
  margin-top: 1rem;
`

const Barriers = ({
  barriers,
  on_network_barriers,
  total_barriers,
  crossings,
}) => {
  const totalRoadBarriers = total_barriers + crossings
  const offNetworkBarriers = barriers - on_network_barriers

  if (totalRoadBarriers === 0) {
    return (
      <HelpText>
        This area does not yet have any road-related barriers that have been
        assessed for impacts to aquatic organisms.
      </HelpText>
    )
  }

  return (
    <>
      This area contains:
      <List>
        <li>
          <b>{formatNumber(totalRoadBarriers, 0)}</b> road-related potential{' '}
          {totalRoadBarriers > 1 ? 'barriers' : 'barrier'}
        </li>
        <li>
          <b>{formatNumber(total_barriers, 0)}</b>{' '}
          {total_barriers > 1 ? 'barriers' : 'barrier'}{' '}
          {total_barriers > 1 ? 'have ' : 'has '} been assessed for impacts to
          aquatic organisms.
        </li>
        <li>
          <b>{formatNumber(barriers, 0)}</b> road-related{' '}
          {barriers > 1 ? 'barriers' : 'barrier'} assessed{' '}
          {barriers > 1 ? 'are' : 'is'} likely to impact aquatic organisms
        </li>
        <li>
          <b>{formatNumber(on_network_barriers, 0)}</b>{' '}
          {on_network_barriers > 1 ? 'dams' : 'dam'} that{' '}
          {on_network_barriers > 1 ? 'were ' : 'was '} analyzed for impacts to
          aquatic connectivity in this tool
        </li>
      </List>
      <HelpText>
        <br />
        <br />
        Note: These statistics are based on <i>inventoried</i> road-related
        barriers that have been assessed for impacts to aquatic organisms.
        Because the inventory is incomplete in many areas, areas with a high
        number of barriers may simply represent areas that have a more complete
        inventory.
        {offNetworkBarriers > 0 ? (
          <>
            <br />
            <br />
            {formatNumber(offNetworkBarriers, 0)}{' '}
            {offNetworkBarriers > 1 ? 'barriers' : 'barrier'} that{' '}
            {offNetworkBarriers > 1 ? 'were ' : 'was '} not analyzed because
            they were not on the aquatic network or could not be correctly
            located on the network
          </>
        ) : null}
      </HelpText>
    </>
  )
}

Barriers.propTypes = {
  barriers: PropTypes.number,
  total_barriers: PropTypes.number,
  on_network_barriers: PropTypes.number,
  crossings: PropTypes.number,
}

Barriers.defaultProps = {
  barriers: 0,
  total_barriers: 0,
  on_network_barriers: 0,
  crossings: 0,
}

export default Barriers
