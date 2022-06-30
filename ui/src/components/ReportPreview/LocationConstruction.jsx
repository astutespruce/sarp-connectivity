import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading } from 'theme-ui'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import { formatNumber } from 'util/format'

import {
  DAM_CONDITION,
  CONSTRUCTION,
  CONSTRICTION,
  PASSAGEFACILITY,
  OWNERTYPE,
  PURPOSE,
  BARRIER_SEVERITY,
  WATERBODY_SIZECLASS,
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
  lowheaddam,
  purpose,
  condition,
  passagefacility,
  estimated,
  year,
  height,
  width,
  roadtype,
  crossingtype,
  constriction,
  severityclass,
  sarp_score,
  diversion,
  waterbodykm2,
  waterbodysizeclass,
  ...props
}) => {
  let barrierTypeLabel = barrierType === 'dams' ? 'dam' : 'road-related barrier'
  if (barrierType === 'dams' && estimated) {
    barrierTypeLabel = 'estimated dam'
  }

  const hasRiver =
    river && river !== '"' && river !== 'null' && river !== 'Unknown'

  const hasOwner = ownertype && ownertype > 0

  return (
    <Box {...props}>
      <Heading as="h3">Location & construction information</Heading>

      <Grid columns={2} gap={4}>
        <Box as="ul">
          <li>Barrier type: {barrierTypeLabel}</li>

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
              {constriction ? (
                <li>Type of constriction: {CONSTRICTION[constriction]}</li>
              ) : null}
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
  river: PropTypes.string,
  intermittent: PropTypes.number,
  subbasin: PropTypes.string,
  subwatershed: PropTypes.string,
  huc8: PropTypes.string,
  huc12: PropTypes.string,
  ownertype: PropTypes.number,
  height: PropTypes.number,
  width: PropTypes.number,
  year: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  passagefacility: PropTypes.number,
  estimated: PropTypes.bool,
  roadtype: PropTypes.string,
  crossingtype: PropTypes.string,
  constriction: PropTypes.number,
  severityclass: PropTypes.number,
  sarp_score: PropTypes.number,
  diversion: PropTypes.number,
  lowheaddam: PropTypes.number,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
}

LocationConstruction.defaultProps = {
  river: null,
  intermittent: 0,
  subbasin: null,
  subwatershed: null,
  huc8: null,
  huc12: null,
  ownertype: null,
  height: 0,
  width: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
  estimated: false,
  roadtype: null,
  crossingtype: null,
  constriction: 0,
  severityclass: null,
  sarp_score: -1,
  diversion: 0,
  lowheaddam: -1,
  waterbodykm2: -1,
  waterbodysizeclass: -1,
}

export default LocationConstruction
