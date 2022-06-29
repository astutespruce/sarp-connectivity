import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { formatNumber } from 'util/format'

const Barriers = ({
  smallBarriers,
  rankedSmallBarriers,
  totalSmallBarriers,
  crossings,
}) => {
  const totalRoadBarriers = totalSmallBarriers + crossings
  const unrankedBarriers = smallBarriers - rankedSmallBarriers

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
          <b>{formatNumber(totalSmallBarriers, 0)}</b> road-related{' '}
          {totalSmallBarriers === 1 ? 'barrier' : 'barriers'}{' '}
          {totalSmallBarriers === 1 ? 'has ' : 'have '} been assessed for
          impacts to aquatic organisms.
        </li>
        <li>
          <b>{formatNumber(smallBarriers, 0)}</b> road-related{' '}
          {smallBarriers === 1 ? 'barrier' : 'barriers'} assessed{' '}
          {smallBarriers === 1 ? 'is' : 'are'} likely to impact aquatic
          organisms
        </li>
        <li>
          <b>{formatNumber(rankedSmallBarriers, 0)}</b> road-related{' '}
          {rankedSmallBarriers === 1 ? 'barrier' : 'barriers'} that{' '}
          {rankedSmallBarriers === 1 ? 'was ' : 'were '} analyzed for impacts to
          aquatic connectivity in this tool
        </li>
      </Box>

      <Paragraph variant="help" sx={{ mt: '2rem' }}>
        Note: These statistics are based on <i>inventoried</i> road-related
        barriers that have been assessed for impacts to aquatic organisms.
        Because the inventory is incomplete in many areas, areas with a high
        number of barriers may simply represent areas that have a more complete
        inventory.
        {unrankedBarriers > 0 ? (
          <>
            <br />
            <br />
            {formatNumber(unrankedBarriers, 0)} road-related{' '}
            {unrankedBarriers === 1 ? 'barrier' : 'barriers'} that{' '}
            {unrankedBarriers === 1 ? 'was ' : 'were '} not analyzed because
            they were not on the aquatic network or could not be correctly
            located on the network
          </>
        ) : null}
      </Paragraph>
    </>
  )
}

Barriers.propTypes = {
  smallBarriers: PropTypes.number,
  totalSmallBarriers: PropTypes.number,
  rankedSmallBarriers: PropTypes.number,
  crossings: PropTypes.number,
}

Barriers.defaultProps = {
  smallBarriers: 0,
  totalSmallBarriers: 0,
  rankedSmallBarriers: 0,
  crossings: 0,
}

export default Barriers
