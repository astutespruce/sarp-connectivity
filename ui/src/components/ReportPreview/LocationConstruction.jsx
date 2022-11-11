import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading } from 'theme-ui'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import {
  CONDITION,
  CONSTRUCTION,
  CONSTRICTION,
  CROSSING_TYPE,
  PASSAGEFACILITY,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  PURPOSE,
  BARRIER_SEVERITY,
  WATERBODY_SIZECLASS,
} from 'config'
import { formatNumber } from 'util/format'

const LocationConstruction = ({
  barrierType,
  river,
  intermittent,
  subbasin,
  subwatershed,
  huc8,
  huc12,
  ownertype,
  barrierownertype,
  construction,
  lowheaddam,
  purpose,
  condition,
  passagefacility,
  estimated,
  yearcompleted,
  height,
  width,
  roadtype,
  crossingtype,
  constriction,
  barrierseverity,
  sarp_score,
  diversion,
  waterbodykm2,
  waterbodysizeclass,
  sx,
}) => {
  let barrierTypeLabel = barrierType === 'dams' ? 'dam' : 'road-related barrier'
  if (barrierType === 'dams' && estimated) {
    barrierTypeLabel = 'estimated dam'
  }

  const hasRiver =
    river && river !== '"' && river !== 'null' && river !== 'Unknown'

  const hasLandOwner = ownertype && ownertype > 0
  const hasBarrierOwner = barrierownertype && barrierownertype > 0

  return (
    <Box sx={sx}>
      <Heading as="h3">Location & construction information</Heading>

      <Grid columns={2} gap={4}>
        <Box as="ul">
          <li>Barrier type: {barrierTypeLabel}</li>

          {barrierType === 'dams' ? (
            <>
              {yearcompleted > 0 ? (
                <li>Constructed completed: {yearcompleted}</li>
              ) : null}
              {height > 0 ? <li>Height: {height} feet</li> : null}
              {width > 0 ? <li>Width: {width} feet</li> : null}
              {construction && CONSTRUCTION[construction] ? (
                <li>
                  Construction material:{' '}
                  {CONSTRUCTION[construction].toLowerCase()}
                </li>
              ) : null}
              {lowheaddam >= 1 ? (
                <li>
                  This is {lowheaddam === 2 ? 'likely' : ''} a lowhead dam
                </li>
              ) : null}
              {diversion === 1 ? (
                <li>Diversion: this is a water diversion</li>
              ) : null}
              {purpose && PURPOSE[purpose] ? (
                <li>Purpose: {PURPOSE[purpose].toLowerCase()}</li>
              ) : null}
              {condition && CONDITION[condition] ? (
                <li>
                  Structural condition: {CONDITION[condition].toLowerCase()}
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
              {crossingtype ? (
                <li>Crossing type: {CROSSING_TYPE[crossingtype]}</li>
              ) : null}
              {constriction ? (
                <li>Type of constriction: {CONSTRICTION[constriction]}</li>
              ) : null}
              {condition ? <li>Condition: {condition}</li> : null}
              {barrierseverity !== null ? (
                <li>Severity: {BARRIER_SEVERITY[barrierseverity]}</li>
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

          {barrierType === 'dams' && waterbodysizeclass >= 0 ? (
            <li>
              Size of associated pond or lake:
              <br />
              {waterbodykm2 > 0.1
                ? `${formatNumber(waterbodykm2, 2)} k`
                : `${formatNumber(waterbodykm2 * 1e6)} `}
              m<sup>2</sup> (
              {WATERBODY_SIZECLASS[waterbodysizeclass]
                .split(' (')[0]
                .toLowerCase()}
              )
            </li>
          ) : null}

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
          {hasLandOwner ? (
            <li>Conservation land type: {OWNERTYPE[ownertype]}</li>
          ) : null}

          {hasBarrierOwner ? (
            <li>
              Barrier ownership type: {BARRIEROWNERTYPE[barrierownertype]}
            </li>
          ) : null}
        </Box>
      </Grid>
    </Box>
  )
}

LocationConstruction.propTypes = {
  barrierType: PropTypes.string.isRequired,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  subbasin: PropTypes.string,
  subwatershed: PropTypes.string,
  huc8: PropTypes.string,
  huc12: PropTypes.string,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  height: PropTypes.number,
  width: PropTypes.number,
  yearcompleted: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  passagefacility: PropTypes.number,
  estimated: PropTypes.bool,
  roadtype: PropTypes.string,
  crossingtype: PropTypes.number,
  constriction: PropTypes.number,
  barrierseverity: PropTypes.number,
  sarp_score: PropTypes.number,
  diversion: PropTypes.number,
  lowheaddam: PropTypes.number,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  sx: PropTypes.object,
}

LocationConstruction.defaultProps = {
  river: null,
  intermittent: 0,
  subbasin: null,
  subwatershed: null,
  huc8: null,
  huc12: null,
  ownertype: null,
  barrierownertype: null,
  height: 0,
  width: 0,
  yearcompleted: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
  estimated: false,
  roadtype: null,
  crossingtype: 0,
  constriction: 0,
  barrierseverity: null,
  sarp_score: -1,
  diversion: 0,
  lowheaddam: -1,
  waterbodykm2: -1,
  waterbodysizeclass: -1,
  sx: null,
}

export default LocationConstruction
