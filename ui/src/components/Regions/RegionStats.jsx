import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { formatNumber } from 'util/format'

const RegionStats = ({
  dams,
  onNetworkDams,
  totalSmallBarriers,
  smallBarriers,
  onNetworkSmallBarriers,
  crossings,
}) => (
  <Box as="ul">
    <li>
      <b>{formatNumber(dams)}</b> inventoried dams
    </li>
    <li>
      <b>{formatNumber(onNetworkDams)}</b> dams that have been analyzed for
      their impacts to aquatic connectivity in this tool
    </li>
    <li>
      <b>{formatNumber(totalSmallBarriers + crossings, 0)}</b> or more potential
      road-related aquatic barriers
    </li>
    <li>
      <b>{formatNumber(totalSmallBarriers, 0)}</b> that have been assessed for
      impacts to aquatic organisms
    </li>
    <li>
      <b>{formatNumber(smallBarriers, 0)}</b> road-related barriers assessed so
      far that are likely to impact aquatic organisms
    </li>
    <li>
      <b>{formatNumber(onNetworkSmallBarriers, 0)}</b> that have been evaluated
      for their impacts to aquatic connectivity in this tool
    </li>
  </Box>
)

RegionStats.propTypes = {
  dams: PropTypes.number.isRequired,
  onNetworkDams: PropTypes.number.isRequired,
  totalSmallBarriers: PropTypes.number.isRequired,
  smallBarriers: PropTypes.number.isRequired,
  onNetworkSmallBarriers: PropTypes.number.isRequired,
  crossings: PropTypes.number.isRequired,
}

export default RegionStats
