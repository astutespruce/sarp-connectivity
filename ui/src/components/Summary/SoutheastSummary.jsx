import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText } from 'components/Text'
import { Box } from 'components/Grid'
import UnitSearch from 'components/UnitSearch'
import { useSummaryData } from 'components/Data'
import { formatNumber } from 'util/format'
import styled, { themeGet } from 'style'

const Wrapper = styled(Box).attrs({ p: '1rem' })``

const Intro = styled(Text).attrs({ mb: '1rem' })``

const Note = styled(HelpText).attrs({ mt: '3rem' })`
  color: ${themeGet('colors.grey.600')};
`

const SoutheastSummary = ({ barrierType, system, onSearch }) => {
  const { dams, miles, barriers, crossings } = useSummaryData()

  if (barrierType === 'dams') {
    return (
      <Wrapper>
        <Intro>
          Across the Southeast, there are at least {formatNumber(dams, 0)} dams,
          resulting in an average of {formatNumber(miles, 0)} miles of connected
          rivers and streams.
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
        Across the Southeast, there are at least {formatNumber(barriers, 0)}{' '}
        road-related barriers and at least {formatNumber(crossings, 0)} road /
        stream crossings.
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
