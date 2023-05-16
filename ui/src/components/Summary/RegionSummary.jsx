/* eslint-disable camelcase */

import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph, Divider } from 'theme-ui'

import { UnitSearch } from 'components/UnitSearch'
import { useSummaryData } from 'components/Data'
import { REGIONS } from 'config'
import { formatNumber } from 'util/format'

const RegionSummary = ({ region, barrierType, system, onSearch }) => {
  const { name } = REGIONS[region]
  const {
    [region]: {
      dams,
      reconDams,
      rankedDams,
      totalSmallBarriers,
      smallBarriers,
      rankedSmallBarriers,
      crossings,
    },
  } = useSummaryData()

  const unrankedDams = dams - rankedDams
  const unrankedBarriers = smallBarriers - rankedSmallBarriers

  const regionName = region === 'total' ? 'full analysis area' : name

  return (
    <Box sx={{ p: '1rem', overflowY: 'auto', height: '100%' }}>
      <Paragraph sx={{ fontSize: [3, 4] }}>
        Across the {regionName}, there are:
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
              <b>{formatNumber(rankedDams, 0)}</b> have been analyzed for their
              impacts to aquatic connectivity in this tool
            </li>
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
          </Box>
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

RegionSummary.propTypes = {
  region: PropTypes.string,
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string.isRequired,
  onSearch: PropTypes.func.isRequired,
}

RegionSummary.defaultProps = {
  region: 'total',
}

export default RegionSummary
