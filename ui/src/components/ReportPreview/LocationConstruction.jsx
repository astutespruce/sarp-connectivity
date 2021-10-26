import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading, Text } from 'theme-ui'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import { formatNumber } from 'util/format'

import {
  DAM_CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  OWNERTYPE,
  PURPOSE,
  BARRIER_SEVERITY,
} from '../../../config/constants'

const LocationConstruction = ({
  barrierType,
  river,
  intermittent,
  subbasin,
  subwatershed,
  huc8,
  huc12,
  ownertype,
  construction,
  purpose,
  condition,
  passagefacility,
  year,
  height,
  width,
  roadtype,
  crossingtype,
  severityclass,
  sarp_score,
  ...props
}) => {
  const hasRiver =
    river && river !== '"' && river !== 'null' && river !== 'Unknown'

  const hasOwner = ownertype && ownertype > 0

  // if (barrierType === 'dams') {
  return (
    <Box {...props}>
      <Heading as="h3">Location & construction information</Heading>

      <Grid columns={2} gap={4}>
        <Box as="ul">
          <li>
            Barrier type:{' '}
            {barrierType === 'dams' ? 'dam' : 'road-related barrier'}
          </li>

          {barrierType === 'dams' ? (
            <>
              {year > 0 ? <li>Constructed completed: {year}</li> : null}
              {height > 0 ? <li>Height: {height} feet</li> : null}
              {width > 0 ? <li>Width: {width} feet</li> : null}
              {construction && CONSTRUCTION[construction] ? (
                <li>
                  Construction material:{' '}
                  {CONSTRUCTION[construction].toLowerCase()}
                </li>
              ) : null}
              {purpose && PURPOSE[purpose] ? (
                <li>Purpose: {PURPOSE[purpose].toLowerCase()}</li>
              ) : null}
              {condition && DAM_CONDITION[condition] ? (
                <li>
                  Structural condition: {DAM_CONDITION[condition].toLowerCase()}
                </li>
              ) : null}

              {PASSAGEFACILITY[passagefacility] ? (
                <li>
                  Passage facility type:{' '}
                  {PASSAGEFACILITY[passagefacility].toLowerCase()}
                </li>
              ) : null}
            </>
          ) : (
            <>
              {roadtype ? <li>Road type: {roadtype}</li> : null}
              {crossingtype ? <li>Crossing type: {crossingtype}</li> : null}
              {condition ? <li>Condition: {condition}</li> : null}
              {severityclass !== null ? (
                <li>Severity: {BARRIER_SEVERITY[severityclass]}</li>
              ) : null}
              {sarp_score >= 0 ? (
                <li>
                  SARP Aquatic Organism Passage Score:{' '}
                  {formatNumber(sarp_score, 1)} ({classifySARPScore(sarp_score)}
                  )
                </li>
              ) : null}
            </>
          )}
        </Box>
        <Box as="ul">
          {hasRiver ? <li>River or stream: {river}</li> : null}

          {intermittent === 1 ? (
            <li>Located on a reach that has intermittent or ephemeral flow</li>
          ) : null}

          {huc12 ? (
            <>
              <li>
                Subwatershed: {subwatershed}
                <br />
                (HUC12: {huc12})
              </li>
              <li>
                Subbasin: {subbasin}
                <br />
                (HUC8: {huc8})
              </li>
            </>
          ) : null}
          {hasOwner ? (
            <li>Conservation land type: {OWNERTYPE[ownertype]}</li>
          ) : null}
        </Box>
      </Grid>
    </Box>
  )
}

LocationConstruction.propTypes = {
  barrierType: PropTypes.string.isRequired,
  height: PropTypes.number,
  width: PropTypes.number,
  year: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  passagefacility: PropTypes.number,
  roadtype: PropTypes.string,
  crossingtype: PropTypes.string,
  severityclass: PropTypes.number,
  sarp_score: PropTypes.number,
}

LocationConstruction.defaultProps = {
  height: 0,
  width: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
  roadtype: null,
  crossingtype: null,
  severityclass: null,
  sarp_score: -1,
}

export default LocationConstruction
