/* eslint-disable camelcase */

import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText } from 'components/Text'
import { Box } from 'components/Grid'
import UnitSearch from 'components/UnitSearch'
import { useSummaryData } from 'components/Data'
import { formatNumber } from 'util/format'
import styled, { themeGet } from 'style'

const Wrapper = styled(Box).attrs({ p: '1rem' })`
  overflow-y: auto;
  height: 100%;
`

const Intro = styled(Text).attrs({ mb: '1rem' })``

const Note = styled(HelpText).attrs({ mt: '3rem' })`
  color: ${themeGet('colors.grey.600')};
`

const SoutheastSummary = ({ barrierType, system, onSearch }) => {
  const {
    dams,
    on_network_dams,
    miles,
    total_barriers,
    barriers,
    on_network_barriers,
    crossings,
  } = useSummaryData()
  const offNetworkDams = dams - on_network_dams
  const offNetworkBarriers = barriers - on_network_barriers

  const totalRoadBarriers = total_barriers + crossings

  if (barrierType === 'dams') {
    return (
      <Wrapper>
        <Intro>
          Across the Southeast, there are at least{' '}
          <b>{formatNumber(dams, 0)}</b> dams inventoried so far.
          <br />
          <br />
          <b>{formatNumber(on_network_dams, 0)}</b> dams have been analyzed for
          their impacts to aquatic connectivity in this tool.
          <br />
          <br />
          <b>{formatNumber(offNetworkDams, 0)}</b> dams were not analyzed
          because they were not on the aquatic network or could not be correctly
          located on the aquatic network.
          <br />
          <br />
          Based on this analysis, there is an average of{' '}
          <b>{formatNumber(miles, 0)}</b> miles of connected rivers and streams
          in the Southeast.
          <br />
          <br />
          Click on a summary unit the map for more information about that area.
        </Intro>
        <UnitSearch system={system} onSelect={onSearch} />

        <Note>
          Note: These statistics are based on <i>inventoried</i> dams. Because
          the inventory is incomplete in many areas, areas with a high number of
          dams may simply represent areas that have a more complete inventory.
        </Note>
      </Wrapper>
    )
  }

  // otherwise barriers
  return (
    <Wrapper>
      <Intro>
        Across the Southeast, there are at least{' '}
        <b>{formatNumber(totalRoadBarriers, 0)}</b> potential road-related
        aquatic barriers. Of these, <b>{formatNumber(total_barriers, 0)}</b>{' '}
        have been assessed for potential impacts to aquatic organisms.
        <br />
        <br />
        <b>{formatNumber(barriers, 0)}</b> road-related barriers assessed so far
        are likely to impact aquatic organisms and{' '}
        <b>{formatNumber(on_network_barriers, 0)}</b> have been evaluated for
        their impacts to aquatic connectivity in this tool.
        <br />
        <br />
        <b>{formatNumber(offNetworkBarriers, 0)}</b> road-related were not
        analyzed because they were not on the aquatic network or could not be
        correctly located on the aquatic network.
        <br />
        <br />
        Click on a summary unit the map for more information about that area.
      </Intro>
      <UnitSearch system={system} onSelect={onSearch} />

      <Note>
        Note: These statistics are based on <i>inventoried</i> road-related
        barriers. Because the inventory is incomplete in many areas, areas with
        a high number of road-related barriers may simply represent areas that
        have a more complete inventory.
      </Note>
    </Wrapper>
  )
}

SoutheastSummary.propTypes = {
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string.isRequired,
  onSearch: PropTypes.func.isRequired,
}

export default memo(SoutheastSummary)
