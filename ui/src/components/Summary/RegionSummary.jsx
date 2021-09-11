/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import UnitSearch from 'components/UnitSearch'
import { useSummaryData } from 'components/Data'
import { formatNumber } from 'util/format'
import { getQueryParams } from 'util/dom'

import { REGIONS } from '../../../config/constants'

const SoutheastSummary = ({ barrierType, system, onSearch }) => {
  const { region = 'total' } = getQueryParams()

  console.log('region', region)

  const {
    [region]: {
      dams,
      onNetworkDams,
      totalSmallBarriers,
      smallBarriers,
      onNetworkSmallBarriers,
      crossings,
    },
  } = useSummaryData()

  const offNetworkDams = dams - onNetworkDams
  const offNetworkBarriers = smallBarriers - onNetworkSmallBarriers
  const totalRoadBarriers = totalSmallBarriers + crossings

  const regionName = region === 'total' ? 'full analysis area' : REGIONS[region]

  if (barrierType === 'dams') {
    return (
      <Box sx={{ p: '1rem', overflowY: 'auto', height: '100%' }}>
        <Paragraph>Across the {regionName}, there are:</Paragraph>
        <Box as="ul" sx={{ mt: '1rem' }}>
          <li>
            <b>{formatNumber(dams, 0)}</b> inventoried dams
          </li>
          <li>
            <b>{formatNumber(onNetworkDams, 0)}</b> dams that have been analyzed
            for their impacts to aquatic connectivity in this tool
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
      <Paragraph>Across the {regionName}, there are:</Paragraph>
      <Box as="ul" sx={{ mt: '1rem' }}>
        <li>
          <b>{formatNumber(totalRoadBarriers, 0)}</b> or more potential
          road-related aquatic barriers
        </li>
        <li>
          <b>{formatNumber(totalSmallBarriers, 0)}</b> that have been assessed
          for impacts to aquatic organisms
        </li>
        <li>
          <b>{formatNumber(smallBarriers, 0)}</b> road-related barriers assessed
          so far that are likely to impact aquatic organisms
        </li>
        <li>
          <b>{formatNumber(onNetworkSmallBarriers, 0)}</b> that have been
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
