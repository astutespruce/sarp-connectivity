/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import UnitSearch from 'components/UnitSearch'
import { useSummaryData } from 'components/Data'
import { formatNumber } from 'util/format'

const SoutheastSummary = ({ barrierType, system, onSearch }) => {
  const {
    se: {
      dams,
      on_network_dams,
      miles,
      total_small_barriers,
      small_barriers,
      on_network_small_barriers,
      crossings,
    },
  } = useSummaryData()
  const offNetworkDams = dams - on_network_dams
  const offNetworkBarriers = small_barriers - on_network_small_barriers

  const totalRoadBarriers = total_small_barriers + crossings

  if (barrierType === 'dams') {
    return (
      <Box sx={{ p: '1rem', overflowY: 'auto', height: '100%' }}>
        <Paragraph>Across the Southeast, there are:</Paragraph>
        <Box as="ul" sx={{ mt: '1rem' }}>
          <li>
            <b>{formatNumber(dams, 0)}</b> inventoried dams
          </li>
          <li>
            <b>{formatNumber(on_network_dams, 0)}</b> dams that have been
            analyzed for their impacts to aquatic connectivity in this tool
          </li>
          <li>
            <b>{formatNumber(miles, 0)}</b> miles of connected rivers and
            streams on average across the region
          </li>
        </Box>

        <Paragraph sx={{ mb: '2rem' }}>
          <br />
          <br />
          Click on a summary unit the map for more information about that area.
        </Paragraph>

        <UnitSearch system={system} onSelect={onSearch} />

        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: These statistics are based on <i>inventoried</i> dams. Because
          the inventory is incomplete in many areas, areas with a high number of
          dams may simply represent areas that have a more complete inventory.
          <br />
          <br />
          {formatNumber(offNetworkDams, 0)} dams were not analyzed because they
          could not be correctly located on the aquatic network or were
          otherwise excluded from the analysis.
        </Paragraph>
      </Box>
    )
  }

  // otherwise barriers
  return (
    <Box sx={{ p: '1rem', overflowY: 'auto', height: '100%' }}>
      <Paragraph>Across the Southeast, there are:</Paragraph>
      <Box as="ul" sx={{ mt: '1rem' }}>
        <li>
          <b>{formatNumber(totalRoadBarriers, 0)}</b> or more potential
          road-related aquatic barriers
        </li>
        <li>
          <b>{formatNumber(total_small_barriers, 0)}</b> that have been assessed
          for impacts to aquatic organisms
        </li>
        <li>
          <b>{formatNumber(small_barriers, 0)}</b> road-related barriers
          assessed so far that are likely to impact aquatic organisms
        </li>
        <li>
          <b>{formatNumber(on_network_small_barriers, 0)}</b> that have been
          evaluated for their impacts to aquatic connectivity in this tool
        </li>
      </Box>

      <Paragraph sx={{ mb: '2rem' }}>
        <br />
        <br />
        Click on a summary unit the map for more information about that area.
      </Paragraph>

      <UnitSearch system={system} onSelect={onSearch} />

      <Paragraph variant="help">
        Note: These statistics are based on <i>inventoried</i> road-related
        barriers. Because the inventory is incomplete in many areas, areas with
        a high number of road-related barriers may simply represent areas that
        have a more complete inventory.
        <br />
        <br />
        {formatNumber(offNetworkBarriers, 0)} road-related barriers could not be
        correctly located on the aquatic network or were otherwise excluded from
        the analysis.
      </Paragraph>
    </Box>
  )
}

SoutheastSummary.propTypes = {
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string.isRequired,
  onSearch: PropTypes.func.isRequired,
}

export default SoutheastSummary
