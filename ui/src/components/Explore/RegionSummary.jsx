/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { AngleDoubleRight } from '@emotion-icons/fa-solid'
import { Box, Paragraph, Divider, Text } from 'theme-ui'

import { Link } from 'components/Link'
import { UnitSearch } from 'components/UnitSearch'
import { useSummaryData, useRegionSummary } from 'components/Data'
import { REGIONS } from 'config'
import { formatNumber } from 'util/format'

const Summary = ({ region, barrierType, system, onSearch }) => {
  let name = 'full analysis area'
  if (region !== 'total') {
    name = REGIONS[region].name
  }

  const summary = useSummaryData()
  const regions = useRegionSummary()
  const isRegion = region !== 'total'

  const {
    dams,
    reconDams,
    rankedDams,
    removedDams,
    removedDamsGainMiles,
    totalSmallBarriers,
    smallBarriers,
    rankedSmallBarriers,
    removedSmallBarriers,
    removedSmallBarriersGainMiles,
    crossings,
  } = isRegion ? regions[region] : summary

  const unrankedDams = dams - rankedDams
  const unrankedBarriers = smallBarriers - rankedSmallBarriers

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
            <b>{formatNumber(dams, 0)}</b> inventoried dams, including:
          </Paragraph>
          <Box as="ul" sx={{ mt: '0.5rem', fontSize: 2 }}>
            <li>
              <b>{formatNumber(reconDams)}</b> that have been reconned for
              social feasibility of removal
            </li>
            <li>
              <b>{formatNumber(rankedDams, 0)}</b> that have been analyzed for
              their impacts to aquatic connectivity in this tool
            </li>
            {removedDams > 0 ? (
              <li>
                <b>{formatNumber(removedDams, 0)}</b> that have been removed or
                mitigated, gaining{' '}
                <b>{formatNumber(removedDamsGainMiles)} miles</b> of reconnected
                rivers and streams
              </li>
            ) : null}
          </Box>
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
            <b>{formatNumber(totalSmallBarriers + crossings, 0)}</b> or more
            potential road-related aquatic barriers, including:
          </Paragraph>
          <Box as="ul" sx={{ mt: '0.5rem', fontSize: 2 }}>
            <li>
              <b>{formatNumber(totalSmallBarriers, 0)}</b> that have been
              assessed for impacts to aquatic organisms
            </li>
            <li>
              <b>{formatNumber(smallBarriers, 0)}</b> that have been assessed so
              far that are likely to impact aquatic organisms
            </li>
            <li>
              <b>{formatNumber(rankedSmallBarriers, 0)}</b> that have been
              analyzed for their impacts to aquatic connectivity in this tool
            </li>
            {removedSmallBarriers > 0 ? (
              <li>
                <b>{formatNumber(removedSmallBarriers, 0)}</b> that have been
                removed or mitigated, gaining{' '}
                <b>{formatNumber(removedSmallBarriersGainMiles)} miles</b> of
                reconnected rivers and streams
              </li>
            ) : null}
          </Box>
        </>
      ) : null}

      <Divider
        sx={{
          borderBottom: '2px solid',
          borderBottomColor: 'grey.3',
          mt: '1.5rem',
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
        clicking on them on the map or searching by name. You can then download
        data for all selected areas.
      </Text>

      <UnitSearch
        barrierType={barrierType}
        system={system}
        onSelect={onSearch}
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
          Note: These statistics are based on <i>inventoried</i> dams. Because
          the inventory is incomplete in many areas, areas with a high number of
          dams may simply represent areas that have a more complete inventory.
          <br />
          <br />
          {formatNumber(unrankedDams, 0)} dams were not analyzed because they
          could not be correctly located on the aquatic network or were
          otherwise excluded from the analysis.
        </Paragraph>
      ) : null}

      {barrierType === 'small_barriers' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on <i>inventoried</i> road-related
          barriers. Because the inventory is incomplete in many areas, areas
          with a high number of road-related barriers may simply represent areas
          that have a more complete inventory.
          <br />
          <br />
          {formatNumber(unrankedBarriers, 0)} road-related barriers could not be
          correctly located on the aquatic network or were otherwise excluded
          from the analysis.
        </Paragraph>
      ) : null}

      {barrierType === 'combined_barriers' ? (
        <Paragraph variant="help" sx={{ mt: '3rem' }}>
          Note: These statistics are based on <i>inventoried</i> dams and
          road-related barriers. Because the inventory is incomplete in many
          areas, areas with a high number of dams or road-related barriers may
          simply represent areas that have a more complete inventory.
          <br />
          <br />
          {formatNumber(unrankedDams, 0)} dams and{' '}
          {formatNumber(unrankedBarriers, 0)} road-related barriers could not be
          correctly located on the aquatic network or were otherwise excluded
          from the analysis.
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
