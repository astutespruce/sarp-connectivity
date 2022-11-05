import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import {
  CONDITION,
  CONSTRUCTION,
  CONSTRICTION,
  CROSSING_TYPE,
  ROAD_TYPE,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  PASSAGEFACILITY,
  PURPOSE,
  BARRIER_SEVERITY,
  WATERBODY_SIZECLASS,
} from 'constants'
import { formatNumber } from 'util/format'

import { Flex, List, ListItem, Section } from './elements'

const Location = ({
  barrierType,
  construction,
  purpose,
  condition,
  lowheaddam,
  passagefacility,
  estimated,
  year,
  height,
  width,
  roadtype,
  crossingtype,
  constriction,
  barrierseverity,
  river,
  intermittent,
  subwatershed,
  subbasin,
  huc12,
  huc8,
  ownertype,
  barrierownertype,
  sarp_score,
  diversion,
  waterbodykm2,
  waterbodysizeclass,
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
    <Section title="Location & construction information" wrap={false}>
      <Flex>
        <View
          style={{
            flex: '1 1 50%',
            marginRight: 36,
          }}
        >
          <List>
            <ListItem>
              <Text>Barrier type: {barrierTypeLabel}</Text>
            </ListItem>
            {barrierType === 'dams' ? (
              <>
                {year > 0 ? (
                  <ListItem>
                    <Text>Constructed completed: {year}</Text>
                  </ListItem>
                ) : null}
                {height > 0 ? (
                  <ListItem>
                    <Text>Height: {height} feet</Text>
                  </ListItem>
                ) : null}
                {width > 0 ? (
                  <ListItem>
                    <Text>Width: {width} feet</Text>
                  </ListItem>
                ) : null}
                {construction && CONSTRUCTION[construction] ? (
                  <ListItem>
                    <Text>
                      Construction material:{' '}
                      {CONSTRUCTION[construction].toLowerCase()}
                    </Text>
                  </ListItem>
                ) : null}
                {lowheaddam >= 1 ? (
                  <ListItem>
                    <Text>
                      This is {lowheaddam === 2 ? 'likely' : ''} a lowhead dam
                    </Text>
                  </ListItem>
                ) : null}
                {diversion === 1 ? (
                  <ListItem>
                    <Text>Diversion: this is a water diversion</Text>
                  </ListItem>
                ) : null}
                {purpose && PURPOSE[purpose] ? (
                  <ListItem>
                    <Text>Purpose: {PURPOSE[purpose].toLowerCase()}</Text>
                  </ListItem>
                ) : null}
                {condition && CONDITION[condition] ? (
                  <ListItem>
                    <Text>
                      Structural condition: {CONDITION[condition].toLowerCase()}
                    </Text>
                  </ListItem>
                ) : null}

                {PASSAGEFACILITY[passagefacility] ? (
                  <ListItem>
                    <Text>
                      Passage facility type:{' '}
                      {PASSAGEFACILITY[passagefacility].toLowerCase()}
                    </Text>
                  </ListItem>
                ) : null}
              </>
            ) : (
              <>
                {roadtype ? (
                  <ListItem>
                    <Text>Road type: {ROAD_TYPE[roadtype]}</Text>
                  </ListItem>
                ) : null}
                {crossingtype ? (
                  <ListItem>
                    <Text>Crossing type: {CROSSING_TYPE[crossingtype]}</Text>
                  </ListItem>
                ) : null}
                {constriction ? (
                  <ListItem>
                    <Text>
                      Type of constriction: {CONSTRICTION[constriction]}
                    </Text>
                  </ListItem>
                ) : null}

                {condition ? (
                  <ListItem>
                    <Text>Condition: {condition}</Text>
                  </ListItem>
                ) : null}

                {barrierseverity !== null ? (
                  <ListItem>
                    <Text>Severity: {BARRIER_SEVERITY[barrierseverity]}</Text>
                  </ListItem>
                ) : null}

                {sarp_score >= 0 ? (
                  <ListItem>
                    <Text>
                      SARP Aquatic Organism Passage Score:{' '}
                      {formatNumber(sarp_score, 1)} (
                      {classifySARPScore(sarp_score)})
                    </Text>
                  </ListItem>
                ) : null}
              </>
            )}
          </List>
        </View>

        <View
          style={{
            flex: '1 1 50%',
          }}
        >
          <List>
            {hasRiver ? (
              <ListItem>
                <Text>River or stream: {river}</Text>
              </ListItem>
            ) : null}

            {barrierType === 'dams' && waterbodysizeclass >= 0 ? (
              <ListItem>
                <Text>Size of associated pond or lake:</Text>
                <Text>
                  {waterbodykm2 > 0.1
                    ? `${formatNumber(waterbodykm2, 2)} k`
                    : `${formatNumber(waterbodykm2 * 1e6)} `}
                  m<sup>2</sup> (
                  {WATERBODY_SIZECLASS[waterbodysizeclass]
                    .split(' (')[0]
                    .toLowerCase()}
                  )
                </Text>
              </ListItem>
            ) : null}

            {intermittent === 1 ? (
              <ListItem>
                <Text>
                  Located on a reach that has intermittent or ephemeral flow
                </Text>
              </ListItem>
            ) : null}

            {huc12 ? (
              <>
                <ListItem>
                  <Text>
                    Subwatershed: {subwatershed} {'\n'} (HUC12: {huc12})
                  </Text>
                </ListItem>
                <ListItem>
                  <Text>
                    Subbasin: {subbasin} {'\n'} (HUC8: {huc8})
                  </Text>
                </ListItem>
              </>
            ) : null}

            {hasLandOwner ? (
              <ListItem>
                <Text>Conservation land type: {OWNERTYPE[ownertype]}</Text>
              </ListItem>
            ) : null}

            {hasBarrierOwner ? (
              <ListItem>
                <Text>
                  Barrier ownership type: {BARRIEROWNERTYPE[barrierownertype]}
                </Text>
              </ListItem>
            ) : null}
          </List>
        </View>
      </Flex>
    </Section>
  )
}

Location.propTypes = {
  barrierType: PropTypes.string.isRequired,
  height: PropTypes.number,
  width: PropTypes.number,
  year: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  passagefacility: PropTypes.number,
  estimated: PropTypes.bool,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  constriction: PropTypes.number,
  barrierseverity: PropTypes.number,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  huc12: PropTypes.string,
  huc8: PropTypes.string,
  subwatershed: PropTypes.string,
  subbasin: PropTypes.string,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  sarp_score: PropTypes.number,
  diversion: PropTypes.number,
  lowheaddam: PropTypes.number,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
}

Location.defaultProps = {
  height: 0,
  width: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
  estimated: false,
  roadtype: 0,
  crossingtype: 0,
  constriction: 0,
  barrierseverity: null,
  river: null,
  intermittent: 0,
  huc12: null,
  huc8: null,
  subwatershed: null,
  subbasin: null,
  ownertype: null,
  barrierownertype: null,
  sarp_score: -1,
  diversion: 0,
  lowheaddam: -1,
  waterbodykm2: -1,
  waterbodysizeclass: -1,
}

export default Location
