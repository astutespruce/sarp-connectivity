import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { formatNumber } from 'util/format'

const RegionStats = ({
  dams,
  reconDams,
  totalSmallBarriers,
  smallBarriers,
  crossings,
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
    </Box>
    <Paragraph sx={{ mt: '2rem' }}>
      <b>{formatNumber(totalSmallBarriers + crossings, 0)}</b> or more potential
      road-related aquatic barriers, including:
    </Paragraph>
    <Box as="ul" sx={{ ml: '1rem', mt: '0.5rem' }}>
      <li>
        <b>{formatNumber(totalSmallBarriers, 0)}</b> that have been assessed for
        impacts to aquatic organisms
      </li>
      <li>
        <b>{formatNumber(smallBarriers, 0)}</b> of these are likely to impact
        aquatic organisms
      </li>
    </Box>
  </Box>
)

RegionStats.propTypes = {
  dams: PropTypes.number.isRequired,
  reconDams: PropTypes.number.isRequired,
  totalSmallBarriers: PropTypes.number.isRequired,
  smallBarriers: PropTypes.number.isRequired,
  crossings: PropTypes.number.isRequired,
}

export default RegionStats
