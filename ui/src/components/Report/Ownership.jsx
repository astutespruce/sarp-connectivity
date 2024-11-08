import React from 'react'
import PropTypes from 'prop-types'
import { Text, View, Link } from '@react-pdf/renderer'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import {
  HAZARD,
  CONDITION,
  CONSTRUCTION,
  CONSTRICTION,
  CROSSING_TYPE,
  ROAD_TYPE,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  FERC_REGULATED,
  STATE_REGULATED,
  WATER_RIGHT,
  PASSAGEFACILITY,
  PURPOSE,
  PASSABILITY,
  SMALL_BARRIER_SEVERITY,
} from 'config'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import { Flex, Entry, Entries, Section } from './elements'

const Ownership = ({
  barrierType,
  ownertype,
  barrierownertype,
  fercregulated,
  stateregulated,
  fedregulatoryagency,
  nrcsdam,
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
  ...props
}) => {
  const hasLandOwner = ownertype && ownertype > 0

  return (
    <Section
      title="Ownership & construction information"
      {...props}
      wrap={false}
    >
      <Flex>
        <View
          style={{
            flex: '1 1 50%',
            marginRight: 24,
          }}
        >
          <Entries>
            {barrierownertype !== null ? (
              <Entry>
                <Text>
                  Barrier ownership type:{' '}
                  {BARRIEROWNERTYPE[barrierownertype].toLowerCase()}
                </Text>
              </Entry>
            ) : null}

            {hasLandOwner ? (
              <Entry>
                <Text>Conservation land type: {OWNERTYPE[ownertype]}</Text>
              </Entry>
            ) : null}

            {fercregulated !== null && fercregulated > 0 ? (
              <Entry>
                <Text>
                  Regulated by the Federal Energy Regulatory Commission:{' '}
                  {FERC_REGULATED[fercregulated].toLowerCase()}
                </Text>
              </Entry>
            ) : null}

            {stateregulated !== null && stateregulated !== -1 ? (
              <Entry>
                <Text>
                  Regulated at the state level:{' '}
                  {STATE_REGULATED[stateregulated].toLowerCase()}
                </Text>
              </Entry>
            ) : null}

            {fedregulatoryagency ? (
              <Entry>
                <Text>Federal regulatory agency: {fedregulatoryagency}</Text>
              </Entry>
            ) : null}

            {nrcsdam === 1 ? (
              <Entry>
                <Text>This is a NRCS flood control dam</Text>
              </Entry>
            ) : null}

            {waterright !== null && waterright > 0 ? (
              <Entry>
                <Text>
                  Has an associated water right:{' '}
                  {WATER_RIGHT[waterright].toLowerCase()}
                </Text>
              </Entry>
            ) : null}

            {fatality > 0 ? (
              <Entry>
                <Text>
                  Number of fatalities recorded: {formatNumber(fatality)}
                </Text>
                <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                  (based on data provided by{' '}
                  <Link href="https://krcproject.groups.et.byu.net/browse.php">
                    Fatalities at Submerged Hydraulic Jumps
                  </Link>
                  )
                </Text>
              </Entry>
            ) : null}

            {costmean && costmean > 0 ? (
              <Entry>
                <Text>
                  Average estimated cost of removal: ${formatNumber(costmean)}
                </Text>
                <Text>
                  (${formatNumber(costlower)} - ${formatNumber(costupper)})
                </Text>
                <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                  Note: costs are modeled based on dam characteristics and are a
                  very rough estimate only; please use with caution. Source:
                  Jumani et. al. (in prep).
                </Text>
              </Entry>
            ) : null}
          </Entries>
        </View>

        <View
          style={{
            flex: '1 1 50%',
            borderLeft: '2px solid #ebedee',
            paddingLeft: '12pt',
          }}
        >
          {barrierType === 'dams' ? (
            <Entries>
              {purpose !== null && purpose >= 0 ? (
                <Entry>
                  <Text>Purpose: {PURPOSE[purpose].toLowerCase()}</Text>
                </Entry>
              ) : null}

              {yearcompleted > 0 ? (
                <Entry>
                  <Text>Constructed completed: {yearcompleted}</Text>
                </Entry>
              ) : null}

              {height > 0 ? (
                <Entry>
                  <Text>Height: {height} feet</Text>
                </Entry>
              ) : null}

              {width > 0 ? (
                <Entry>
                  <Text>Width: {width} feet</Text>
                </Entry>
              ) : null}

              {storagevolume !== null ? (
                <Entry>
                  <Text>
                    Normal storage volume: {formatNumber(storagevolume)}{' '}
                    acre/feet
                  </Text>
                </Entry>
              ) : null}

              {construction !== null && construction >= 0 ? (
                <Entry>
                  <Text>
                    Construction material:{' '}
                    {CONSTRUCTION[construction].toLowerCase()}
                  </Text>
                </Entry>
              ) : null}

              {hazard !== null && hazard > 0 ? (
                <Entry>
                  <Text>Hazard rating: {HAZARD[hazard].toLowerCase()}</Text>
                </Entry>
              ) : null}

              {condition !== null && condition >= 0 ? (
                <Entry>
                  <Text>
                    Structural condition: {CONDITION[condition].toLowerCase()}
                  </Text>
                </Entry>
              ) : null}

              {!removed && passability !== null ? (
                <Entry>
                  <Text>Passability: {PASSABILITY[passability]}</Text>
                </Entry>
              ) : null}

              {passagefacility !== null && passagefacility >= 0 ? (
                <Entry>
                  <Text>
                    Passage facility type:{' '}
                    {PASSAGEFACILITY[passagefacility].toLowerCase()}
                  </Text>
                </Entry>
              ) : null}
            </Entries>
          ) : (
            <Entries>
              {roadtype !== null && roadtype >= 0 ? (
                <Entry>
                  <Text>Road type: {ROAD_TYPE[roadtype]}</Text>
                </Entry>
              ) : null}
              {crossingtype !== null && crossingtype >= 0 ? (
                <Entry>
                  <Text>Crossing type: {CROSSING_TYPE[crossingtype]}</Text>
                </Entry>
              ) : null}
              {constriction !== null && constriction >= 0 ? (
                <Entry>
                  <Text>
                    Type of constriction: {CONSTRICTION[constriction]}
                  </Text>
                </Entry>
              ) : null}

              {condition !== null && condition >= 0 ? (
                <Entry>
                  <Text>Condition: {CONDITION[condition]}</Text>
                </Entry>
              ) : null}

              {!removed && barrierseverity !== null && barrierseverity >= 0 ? (
                <Entry>
                  <Text>
                    Severity: {SMALL_BARRIER_SEVERITY[barrierseverity]}
                  </Text>
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
                    <Text style={{ marginTop: '6pt' }}>
                      Protocol used: {protocolused}
                    </Text>
                  ) : null}
                </Entry>
              ) : null}

              {passagefacility !== null && passagefacility >= 0 ? (
                <Entry>
                  <Text>
                    Passage facility type:{' '}
                    {PASSAGEFACILITY[passagefacility].toLowerCase()}
                  </Text>
                </Entry>
              ) : null}
            </Entries>
          )}
        </View>
      </Flex>
    </Section>
  )
}

Ownership.propTypes = {
  barrierType: PropTypes.string.isRequired,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  fercregulated: PropTypes.number,
  stateregulated: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  nrcsdam: PropTypes.number,
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
}

Ownership.defaultProps = {
  ownertype: null,
  barrierownertype: null,
  fercregulated: null,
  stateregulated: null,
  fedregulatoryagency: null,
  nrcsdam: null,
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
}

export default Ownership
