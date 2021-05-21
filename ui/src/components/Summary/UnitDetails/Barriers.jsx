/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { formatNumber } from 'util/format'

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
      <Paragraph variant="help">
        This area does not yet have any road-related barriers that have been
        assessed for impacts to aquatic organisms.
      </Paragraph>
    )
  }

  return (
    <>
      <Paragraph>This area contains:</Paragraph>

      <Box as="ul" sx={{ mt: '1rem' }}>
        <li>
          <b>{formatNumber(totalRoadBarriers, 0)}</b> road-related potential{' '}
          {totalRoadBarriers === 1 ? 'barrier' : 'barriers'}
        </li>
        <li>
          <b>{formatNumber(total_barriers, 0)}</b> road-related{' '}
          {total_barriers === 1 ? 'barrier' : 'barriers'}{' '}
          {total_barriers === 1 ? 'has ' : 'have '} been assessed for impacts to
          aquatic organisms.
        </li>
        <li>
          <b>{formatNumber(barriers, 0)}</b> road-related{' '}
          {barriers === 1 ? 'barrier' : 'barriers'} assessed{' '}
          {barriers === 1 ? 'is' : 'are'} likely to impact aquatic organisms
        </li>
        <li>
          <b>{formatNumber(on_network_barriers, 0)}</b> road-related{' '}
          {on_network_barriers === 1 ? 'barrier' : 'barriers'} that{' '}
          {on_network_barriers === 1 ? 'was ' : 'were '} analyzed for impacts to
          aquatic connectivity in this tool
        </li>
      </Box>

      <Paragraph variant="help" sx={{ mt: '2rem' }}>
        Note: These statistics are based on <i>inventoried</i> road-related
        barriers that have been assessed for impacts to aquatic organisms.
        Because the inventory is incomplete in many areas, areas with a high
        number of barriers may simply represent areas that have a more complete
        inventory.
        {offNetworkBarriers > 0 ? (
          <>
            <br />
            <br />
            {formatNumber(offNetworkBarriers, 0)} road-related{' '}
            {offNetworkBarriers === 1 ? 'barrier' : 'barriers'} that{' '}
            {offNetworkBarriers === 1 ? 'was ' : 'were '} not analyzed because
            they were not on the aquatic network or could not be correctly
            located on the network
          </>
        ) : null}
      </Paragraph>
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
