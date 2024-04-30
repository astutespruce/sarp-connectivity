import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { formatNumber } from 'util/format'

const RegionStats = ({
  dams,
  reconDams,
  removedDams,
  removedDamsGainMiles,
  totalSmallBarriers,
  smallBarriers,
  removedSmallBarriers,
  removedSmallBarriersGainMiles,
  unsurveyedRoadCrossings,
}) => (
  <Box>
    <Paragraph>
      <b>{formatNumber(dams)}</b> inventoried dams, including:
    </Paragraph>
    <Box as="ul" sx={{ ml: '1rem', mb: '1rem', mt: '0.5rem' }}>
      <li>
        <b>{formatNumber(reconDams)}</b> that have been reconned for social
        feasibility of removal
      </li>
      {removedDams > 0 ? (
        <li>
          <b>{formatNumber(removedDams, 0)}</b> that have been removed or
          mitigated, gaining <b>{formatNumber(removedDamsGainMiles)} miles</b>{' '}
          of reconnected rivers and streams
        </li>
      ) : null}
    </Box>
    <Paragraph sx={{ mt: '2rem' }}>
      <b>{formatNumber(totalSmallBarriers + unsurveyedRoadCrossings, 0)}</b> or
      more potential road-related aquatic barriers, including:
    </Paragraph>
    <Box as="ul" sx={{ ml: '1rem', mt: '0.5rem' }}>
      <li>
        <b>{formatNumber(totalSmallBarriers, 0)}</b> that have been assessed for
        impacts to aquatic organisms
      </li>

      <li>
        <b>{formatNumber(smallBarriers, 0)}</b> that are likely to impact
        aquatic organisms
      </li>
      {removedSmallBarriers > 0 ? (
        <li>
          <b>{formatNumber(removedSmallBarriers, 0)}</b> that have been removed
          or mitigated, gaining{' '}
          <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of
          reconnected rivers and streams
        </li>
      ) : null}
    </Box>
  </Box>
)

RegionStats.propTypes = {
  dams: PropTypes.number.isRequired,
  reconDams: PropTypes.number.isRequired,
  removedDams: PropTypes.number,
  removedDamsGainMiles: PropTypes.number,
  totalSmallBarriers: PropTypes.number.isRequired,
  smallBarriers: PropTypes.number.isRequired,
  removedSmallBarriers: PropTypes.number,
  removedSmallBarriersGainMiles: PropTypes.number,
  unsurveyedRoadCrossings: PropTypes.number.isRequired,
}

RegionStats.defaultProps = {
  removedDams: 0,
  removedDamsGainMiles: 0,
  removedSmallBarriers: 0,
  removedSmallBarriersGainMiles: 0,
}

export default RegionStats
