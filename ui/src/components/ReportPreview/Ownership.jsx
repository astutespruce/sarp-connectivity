import React from 'react'
import PropTypes from 'prop-types'
import { Box, Grid, Heading, Text } from 'theme-ui'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import {
  HAZARD,
  CONDITION,
  CONSTRUCTION,
  CONSTRICTION,
  CROSSING_TYPE,
  PASSAGEFACILITY,
  ROAD_TYPE,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  FERC_REGULATED,
  STATE_REGULATED,
  WATER_RIGHT,
  PURPOSE,
  PASSABILITY,
  SMALL_BARRIER_SEVERITY,
} from 'config'
import { OutboundLink } from 'components/Link'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'
import { Entry } from './elements'

const Ownership = ({
  barrierType,
  ownertype,
  barrierownertype,
  fercregulated,
  stateregulated,
  fedregulatoryagency,
  waterright,
  hazard,
  construction,
  purpose,
  condition,
  passagefacility,
  yearcompleted,
  height,
  width,
  roadtype,
  crossingtype,
  constriction,
  passability,
  barrierseverity,
  sarp_score,
  storagevolume,
  removed,
  costlower,
  costmean,
  costupper,
  fatality,
  protocolused,
  sx,
}) => {
  const hasLandOwner = ownertype && ownertype > 0

  return (
    <Box sx={sx}>
      <Heading as="h3">Ownership & construction information</Heading>

      <Grid columns={2} gap={0}>
        <Box sx={{ mr: '1rem' }}>
          {barrierownertype !== null ? (
            <Entry>
              Barrier ownership type:{' '}
              {BARRIEROWNERTYPE[barrierownertype].toLowerCase()}
            </Entry>
          ) : null}

          {hasLandOwner ? (
            <Entry>Conservation land type: {OWNERTYPE[ownertype]}</Entry>
          ) : null}

          {fercregulated !== null && fercregulated > 0 ? (
            <Entry>
              Regulated by the Federal Energy Regulatory Commission:{' '}
              {FERC_REGULATED[fercregulated].toLowerCase()}
            </Entry>
          ) : null}

          {stateregulated !== null && stateregulated !== -1 ? (
            <Entry>
              Regulated at the state level:{' '}
              {STATE_REGULATED[stateregulated].toLowerCase()}
            </Entry>
          ) : null}

          {fedregulatoryagency ? (
            <Entry>Federal regulatory agency: {fedregulatoryagency}</Entry>
          ) : null}

          {waterright !== null && waterright > 0 ? (
            <Entry>
              Has an associated water right:{' '}
              {WATER_RIGHT[waterright].toLowerCase()}
            </Entry>
          ) : null}

          {fatality > 0 ? (
            <Entry>
              Number of fatalities recorded: {formatNumber(fatality)}
              <Text sx={{ fontSize: 0, color: 'grey.7' }}>
                (based on data provided by{' '}
                <OutboundLink to="https://krcproject.groups.et.byu.net/browse.php">
                  Fatalities at Submerged Hydraulic Jumps
                </OutboundLink>
                )
              </Text>
            </Entry>
          ) : null}

          {costmean && costmean > 0 ? (
            <Entry>
              Average estimated cost of removal: ${formatNumber(costmean)}
              <br /> (${formatNumber(costlower)} - ${formatNumber(costupper)})
              <Text
                sx={{
                  mt: '0.5rem',
                  fontSize: 0,
                  color: 'grey.7',
                  lineHeight: 1.1,
                }}
              >
                Note: costs are modeled based on dam characteristics and are a
                very rough estimate only; please use with caution. Source:
                Jumani et. al. (in prep).
              </Text>
            </Entry>
          ) : null}
        </Box>

        <Box
          sx={{
            borderLeft: '2px solid',
            borderLeftColor: 'grey.1',
            pl: '1rem',
          }}
        >
          {barrierType === 'dams' ? (
            <>
              {purpose !== null && purpose >= 0 ? (
                <Entry>Purpose: {PURPOSE[purpose].toLowerCase()}</Entry>
              ) : null}
              {yearcompleted > 0 ? (
                <Entry>Constructed completed: {yearcompleted}</Entry>
              ) : null}

              {height > 0 ? <Entry>Height: {height} feet</Entry> : null}

              {width > 0 ? <Entry>Width: {width} feet</Entry> : null}

              {storagevolume !== null ? (
                <Entry>
                  Normal storage volume: {formatNumber(storagevolume)} acre/feet
                </Entry>
              ) : null}

              {construction !== null && construction >= 0 ? (
                <Entry>
                  Construction material:{' '}
                  {CONSTRUCTION[construction].toLowerCase()}
                </Entry>
              ) : null}

              {hazard !== null && hazard > 0 ? (
                <Entry>Hazard rating: {HAZARD[hazard].toLowerCase()}</Entry>
              ) : null}

              {condition !== null && condition >= 0 ? (
                <Entry>
                  Structural condition: {CONDITION[condition].toLowerCase()}
                </Entry>
              ) : null}

              {!removed && passability !== null ? (
                <Entry>Passability: {PASSABILITY[passability]}</Entry>
              ) : null}

              {passagefacility !== null && passagefacility >= 0 ? (
                <Entry>
                  Passage facility type:{' '}
                  {PASSAGEFACILITY[passagefacility].toLowerCase()}
                </Entry>
              ) : null}
            </>
          ) : (
            <>
              {roadtype !== null && roadtype >= 0 ? (
                <Entry>Road type: {ROAD_TYPE[roadtype]}</Entry>
              ) : null}
              {crossingtype !== null && crossingtype >= 0 ? (
                <Entry>Crossing type: {CROSSING_TYPE[crossingtype]}</Entry>
              ) : null}
              {constriction !== null && constriction >= 0 ? (
                <Entry>
                  Type of constriction: {CONSTRICTION[constriction]}
                </Entry>
              ) : null}
              {condition !== null && condition >= 0 ? (
                <Entry>Condition: {CONDITION[condition]}</Entry>
              ) : null}
              {!removed && barrierseverity !== null ? (
                <Entry>
                  Severity: {SMALL_BARRIER_SEVERITY[barrierseverity]}
                </Entry>
              ) : null}

              {!removed && sarp_score >= 0 ? (
                <Entry>
                  <Text>
                    SARP Aquatic Organism Passage Score:{' '}
                    {formatNumber(sarp_score, 1)} (
                    {classifySARPScore(sarp_score)})
                  </Text>
                  {!isEmptyString(protocolused) ? (
                    <Text sx={{ mt: '1rem' }}>
                      Protocol used: {protocolused}
                    </Text>
                  ) : null}
                </Entry>
              ) : null}

              {passagefacility !== null && passagefacility >= 0 ? (
                <Entry>
                  Passage facility type:{' '}
                  {PASSAGEFACILITY[passagefacility].toLowerCase()}
                </Entry>
              ) : null}
            </>
          )}
        </Box>
      </Grid>
    </Box>
  )
}

Ownership.propTypes = {
  barrierType: PropTypes.string.isRequired,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  fercregulated: PropTypes.number,
  stateregulated: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  waterright: PropTypes.number,
  height: PropTypes.number,
  width: PropTypes.number,
  yearcompleted: PropTypes.number,
  hazard: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passagefacility: PropTypes.number,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  constriction: PropTypes.number,
  passability: PropTypes.number,
  barrierseverity: PropTypes.number,
  sarp_score: PropTypes.number,
  storagevolume: PropTypes.number,
  removed: PropTypes.bool,
  costlower: PropTypes.number,
  costmean: PropTypes.number,
  costupper: PropTypes.number,
  fatality: PropTypes.number,
  protocolused: PropTypes.string,
  sx: PropTypes.object,
}

Ownership.defaultProps = {
  ownertype: null,
  barrierownertype: null,
  fercregulated: null,
  stateregulated: null,
  fedregulatoryagency: null,
  waterright: null,
  height: 0,
  width: 0,
  hazard: null,
  yearcompleted: 0,
  construction: null,
  purpose: null,
  condition: null,
  passagefacility: null,
  roadtype: null,
  crossingtype: null,
  constriction: null,
  passability: null,
  barrierseverity: null,
  sarp_score: -1,
  storagevolume: null,
  removed: false,
  costlower: 0,
  costmean: 0,
  costupper: 0,
  fatality: 0,
  protocolused: null,
  sx: null,
}

export default Ownership
