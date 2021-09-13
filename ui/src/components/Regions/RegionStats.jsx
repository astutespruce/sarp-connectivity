import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { formatNumber } from 'util/format'

const RegionStats = ({ dams, reconDams, totalSmallBarriers, crossings }) => (
  <Box as="ul">
    <li>
      <b>{formatNumber(dams)}</b> inventoried dams, including:
    </li>
    <Box as="ul" sx={{ ml: '1rem', mb: '1rem' }}>
      <li>
        <b>{formatNumber(reconDams)}</b> dams that have been reconned for social
        feasibility of removal
      </li>
    </Box>
    <li>
      <b>{formatNumber(totalSmallBarriers + crossings, 0)}</b> or more potential
      road-related aquatic barriers, including:
    </li>
    <Box as="ul" sx={{ ml: '1rem' }}>
      <li>
        <b>{formatNumber(totalSmallBarriers, 0)}</b> that have been assessed for
        impacts to aquatic organisms
      </li>
    </Box>
  </Box>
)

RegionStats.propTypes = {
  dams: PropTypes.number.isRequired,
  reconDams: PropTypes.number.isRequired,
  totalSmallBarriers: PropTypes.number.isRequired,
  crossings: PropTypes.number.isRequired,
}

export default RegionStats
