/* eslint-disable camelcase */

import React, { useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'
import { Box, Paragraph, Divider, Text } from 'theme-ui'

import { Link } from 'components/Link'
import { UnitSearch } from 'components/UnitSearch'
import { formatNumber, pluralize } from 'util/format'

import Chart from './Chart'

const Summary = ({
  url,
  urlLabel,
  name,
  barrierType,
  system,
  metric,
  dams,
  removedDams,
  removedDamsGainMiles,
  totalSmallBarriers,
  removedSmallBarriers,
  removedSmallBarriersGainMiles,
  removedBarriersByYear,
  onSelectUnit,
  onChangeMetric,
}) => {
  const contentNodeRef = useRef(null)

  useEffect(() => {
    // force scroll to top on change
    if (contentNodeRef.current !== null) {
      contentNodeRef.current.scrollTo(0, 0)
    }
  }, [])

  return (
    <Box
      ref={contentNodeRef}
      sx={{
        pt: '0.5rem',
        pb: '1rem',
        px: '1rem',
        overflowY: 'auto',
        height: '100%',
      }}
    >
      {url ? (
        <Box sx={{ mb: '1rem' }}>
          <Link to={url}>
            {urlLabel} <AngleDoubleRight size="1em" />
          </Link>
        </Box>
      ) : null}

      <Paragraph sx={{ fontSize: [3, 4] }}>Across {name}, there are:</Paragraph>

      {barrierType === 'dams' || barrierType === 'combined_barriers' ? (
        <>
          <Paragraph sx={{ mt: '0.5rem' }}>
            {removedDams > 0 ? (
              <>
                <b>{formatNumber(removedDams, 0)}</b>{' '}
                {pluralize('dam', removedDams)} that{' '}
                {removedDams === 1
                  ? 'has been or is actively being'
                  : 'have been or are actively being'}{' '}
                removed or mitigated, gaining{' '}
                <b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected
                rivers and streams
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
                {pluralize('road-related barrier', removedSmallBarriers)} that{' '}
                {removedSmallBarriers === 1
                  ? 'has been or is being'
                  : 'have been or are being'}{' '}
                removed or mitigated, gaining{' '}
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

      <Box sx={{ mt: '2rem' }}>
        <Chart
          barrierType={barrierType}
          removedBarriersByYear={removedBarriersByYear}
          metric={metric}
          onChangeMetric={onChangeMetric}
        />
      </Box>

      <Divider
        sx={{
          borderBottom: '2px solid',
          borderBottomColor: 'grey.3',
          mt: '3rem',
          mb: '2rem',
        }}
      />

      <Text
        variant="help"
        sx={{
          mt: '0.5rem',
          pb: '1.5rem',
        }}
      >
        Select {system === 'ADM' ? 'states / counties' : 'hydrologic units'} by
        clicking on them on the map or searching by name.
      </Text>

      <UnitSearch
        barrierType={barrierType}
        system={system}
        onSelect={onSelectUnit}
      />

      <Divider
        sx={{
          borderBottom: '2px solid',
          borderBottomColor: 'grey.3',
          mt: '3rem',
        }}
      />

      {barrierType === 'dams' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>{' '}
          inventoried {pluralize('dam', dams)}, and available information on
          dams that have been or are actively being removed or mitigated,
          including projects starting in 2024. Because the inventory is
          incomplete in many areas, areas with a high number of dams may simply
          represent areas that have a more complete inventory.
        </Paragraph>
      ) : null}

      {barrierType === 'small_barriers' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on{' '}
          <b>{formatNumber(totalSmallBarriers, 0)}</b> inventoried{' '}
          {pluralize('road-related barrier', totalSmallBarriers)}, and available
          information on barriers that have been or are actively being removed
          or mitigated, including projects starting in 2024. Because the
          inventory is incomplete in many areas, areas with a high number of
          road-related barriers may simply represent areas that have a more
          complete inventory.
        </Paragraph>
      ) : null}

      {barrierType === 'combined_barriers' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on <b>{formatNumber(dams, 0)}</b>{' '}
          inventoried {pluralize('dam', dams)} and{' '}
          <b>{formatNumber(totalSmallBarriers, 0)}</b> inventoried{' '}
          {pluralize('road-related barrier', totalSmallBarriers)}, and available
          information on dams and barriers that have been or are actively being
          removed or mitigated, including projects starting in 2024. Because the
          inventory is incomplete in many areas, areas with a high number of
          dams or road-related barriers may simply represent areas that have a
          more complete inventory.
        </Paragraph>
      ) : null}

      <Paragraph variant="help" sx={{ mt: '1rem' }}>
        Miles gained are based on aquatic networks cut by{' '}
        {barrierType === 'dams'
          ? 'waterfalls and dams'
          : 'waterfalls, dams, and road-related barriers'}{' '}
        that were present at the time a given barrier was removed, with the
        exception of those directly upstream that were removed in the same year
        as a given barrier.
      </Paragraph>
    </Box>
  )
}

Summary.propTypes = {
  url: PropTypes.string,
  urlLabel: PropTypes.string,
  name: PropTypes.string.isRequired,
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string.isRequired,
  metric: PropTypes.string.isRequired,
  dams: PropTypes.number,
  removedDams: PropTypes.number,
  removedDamsGainMiles: PropTypes.number,
  totalSmallBarriers: PropTypes.number,
  removedSmallBarriers: PropTypes.number,
  removedSmallBarriersGainMiles: PropTypes.number,
  removedBarriersByYear: PropTypes.array, // validated by Chart.jsx
  onSelectUnit: PropTypes.func.isRequired,
  onChangeMetric: PropTypes.func.isRequired,
}

Summary.defaultProps = {
  url: null,
  urlLabel: null,
  dams: 0,
  removedDams: 0,
  removedDamsGainMiles: 0,
  totalSmallBarriers: 0,
  removedSmallBarriers: 0,
  removedSmallBarriersGainMiles: 0,
  removedBarriersByYear: null,
}

export default Summary
