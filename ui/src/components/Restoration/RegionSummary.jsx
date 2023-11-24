/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'
import { Box, Paragraph, Divider } from 'theme-ui'

import { Link } from 'components/Link'
import { UnitSearch } from 'components/UnitSearch'
import { useSummaryData } from 'components/Data'
import { REGIONS } from 'config'
import { formatNumber, pluralize } from 'util/format'

const Summary = ({ region, barrierType, system, onSearch }) => {
  let name = 'full analysis area'
  if (region !== 'total') {
    name = REGIONS[region].name
  }

  const {
    [region]: {
      dams,
      removedDams,
      removedDamsGainMiles,
      totalSmallBarriers,
      removedSmallBarriers,
      removedSmallBarriersGainMiles,
    },
  } = useSummaryData()

  const isRegion = region !== 'total'

  const regionName = isRegion ? name : 'full analysis area'

  return (
    <Box
      sx={{
        pt: '0.5rem',
        pb: '1rem',
        px: '1rem',
        overflowY: 'auto',
        height: '100%',
      }}
    >
      {isRegion ? (
        <Box sx={{ mb: '1rem' }}>
          <Link to={REGIONS[region].url}>
            view region page for more information{' '}
            <AngleDoubleRight size="1em" />
          </Link>
        </Box>
      ) : null}

      <Paragraph sx={{ fontSize: [3, 4] }}>
        Across the {regionName}
        {region !== 'total' ? ' Region' : null}, there are:
      </Paragraph>

      {barrierType === 'dams' || barrierType === 'combined_barriers' ? (
        <>
          <Paragraph sx={{ mt: '0.5rem' }}>
            {removedDams > 0 ? (
              <>
                <b>{formatNumber(removedDams, 0)}</b>{' '}
                {pluralize('dam', removedDams)} that{' '}
                {removedDams === 1 ? 'has' : 'have'} been removed or mitigated,
                gaining <b>{formatNumber(removedDamsGainMiles)} miles</b> of
                reconnected rivers and streams
              </>
            ) : (
              <>
                <b>0</b> dams that are known to have been removed or mitigated
              </>
            )}
          </Paragraph>
        </>
      ) : null}

      {barrierType === 'small_barriers' ||
      barrierType === 'combined_barriers' ? (
        <>
          <Paragraph
            sx={{
              mt: barrierType === 'combined_barriers' ? '1.5rem' : '0.5rem',
            }}
          >
            {removedSmallBarriers > 0 ? (
              <>
                <b>{formatNumber(removedSmallBarriers, 0)}</b>{' '}
                {pluralize('road-related barrier', removedSmallBarriers)} that
                have been removed or mitigated, gaining{' '}
                <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of
                reconnected rivers and streams
              </>
            ) : (
              <>
                <b>0</b> road-related barriers that are known to have been
                removed or mitigated
              </>
            )}
          </Paragraph>
        </>
      ) : null}

      <Divider
        sx={{
          borderBottom: '2px solid',
          borderBottomColor: 'grey.3',
          mt: '1.5rem',
          mb: '1rem',
        }}
      />

      <Paragraph sx={{ mb: '2rem' }}>
        Click on a summary unit the map for more information about that area.
      </Paragraph>

      <UnitSearch
        barrierType={barrierType}
        system={system}
        onSelect={onSearch}
      />

      {barrierType === 'dams' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on {formatNumber(dams, 0)}{' '}
          inventoried {pluralize('dam', dams)}. Because the inventory is
          incomplete in many areas, areas with a high number of dams may simply
          represent areas that have a more complete inventory.
        </Paragraph>
      ) : null}

      {barrierType === 'small_barriers' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on{' '}
          {formatNumber(totalSmallBarriers, 0)} inventoried{' '}
          {pluralize('road-related barrier', totalSmallBarriers)}. Because the
          inventory is incomplete in many areas, areas with a high number of
          road-related barriers may simply represent areas that have a more
          complete inventory.
        </Paragraph>
      ) : null}

      {barrierType === 'combined_barriers' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on {formatNumber(dams, 0)}{' '}
          inventoried {pluralize('dam', dams)} and{' '}
          {formatNumber(totalSmallBarriers, 0)} inventoried{' '}
          {pluralize('road-related barrier', totalSmallBarriers)}. Because the
          inventory is incomplete in many areas, areas with a high number of
          dams or road-related barriers may simply represent areas that have a
          more complete inventory.
        </Paragraph>
      ) : null}
    </Box>
  )
}

Summary.propTypes = {
  region: PropTypes.string,
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string.isRequired,
  onSearch: PropTypes.func.isRequired,
}

Summary.defaultProps = {
  region: 'total',
}

export default Summary