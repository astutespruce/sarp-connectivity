import React from 'react'
import PropTypes from 'prop-types'
import { Text, View, Svg, Path, Link } from '@react-pdf/renderer'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import {
  siteMetadata,
  barrierTypeLabelSingular,
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
  STREAM_SIZECLASS,
  STREAM_SIZECLASS_DRAINAGE_AREA,
  WATERBODY_SIZECLASS,
} from 'config'
import { formatNumber } from 'util/format'

import { Flex, Entry, Entries, Section } from './elements'

const { version: dataVersion } = siteMetadata

const Location = ({
  barrierType,
  sarpid,
  construction,
  purpose,
  condition,
  lowheaddam,
  passagefacility,
  estimated,
  yearcompleted,
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
  ownertype,
  barrierownertype,
  sarp_score,
  diversion,
  nostructure,
  streamorder,
  streamsizeclass,
  waterbodykm2,
  waterbodysizeclass,
  invasive,
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

  const hasRiver =
    river &&
    river !== '"' &&
    river !== 'null' &&
    river.toLowerCase() !== 'unknown' &&
    river.toLowerCase() !== 'unnamed'

  const hasLandOwner = ownertype && ownertype > 0
  const hasBarrierOwner = barrierownertype && barrierownertype > 0
  const isLowheadDam = lowheaddam !== null && lowheaddam >= 1
  const isDiversion = diversion !== null && diversion >= 1

  return (
    <Section title="Location & construction information" wrap={false}>
      <Flex>
        <View
          style={{
            flex: '1 1 50%',
            marginRight: 24,
          }}
        >
          <Entries>
            <Entry>
              {estimated ? (
                <Flex style={{ alignItems: 'flex-start' }}>
                  <View
                    style={{
                      flex: '0 0 auto',
                      marginTop: '3pt',
                    }}
                  >
                    <Svg viewBox="0 0 576 512" width="20pt" height="20pt">
                      <Path
                        d="M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346 7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"
                        fill="#bec4c8"
                      />
                    </Svg>
                  </View>
                  <Text
                    style={{
                      flex: '1 1 auto',
                      lineHeight: 1.1,
                      marginLeft: '24pt',
                    }}
                  >
                    Dam is estimated from other data sources and may be
                    incorrect; please{' '}
                    <Link
                      href={`mailto:Kat@southeastaquatics.net?subject=Problem with Estimated Dam ${sarpid} (data version: ${dataVersion})`}
                    >
                      let us know
                    </Link>
                  </Text>
                </Flex>
              ) : (
                <Text>
                  Barrier Type:
                  {isLowheadDam ? (
                    <>
                      {lowheaddam === 2 ? 'likely ' : null}
                      lowhead dam
                    </>
                  ) : null}
                  {isDiversion ? (
                    <>
                      {isLowheadDam ? ', ' : null}
                      {diversion === 2 ? 'likely ' : null} water diversion
                      {nostructure
                        ? ' (no associated barrier structure)'
                        : null}
                    </>
                  ) : null}
                  {!(isLowheadDam || isDiversion) ? (
                    <> {barrierTypeLabel}</>
                  ) : null}
                  {invasive ? ', invasive species barrier' : null}
                </Text>
              )}
            </Entry>

            <Entry>
              <Text>
                {hasRiver ? `On ${river} in` : 'Within'} {subwatershed}{' '}
                Subwatershed, {subbasin} Subbasin
                <br />
                HUC12: {huc12}
              </Text>
            </Entry>

            {intermittent ? (
              <Entry>
                <Text>
                  This {barrierTypeLabel} is located on a reach that has
                  intermittent or ephemeral flow
                </Text>
              </Entry>
            ) : null}

            {barrierType === 'dams' &&
            waterbodysizeclass !== null &&
            waterbodysizeclass > 0 ? (
              <Entry>
                <Text>
                  This {barrierTypeLabel} is associated with a{' '}
                  {WATERBODY_SIZECLASS[waterbodysizeclass]
                    .split(' (')[0]
                    .toLowerCase()}{' '}
                  (
                  {waterbodykm2 > 0.1
                    ? `${formatNumber(waterbodykm2, 2)} k`
                    : `${formatNumber(waterbodykm2 * 1e6)} `}
                  m2 ).
                </Text>
              </Entry>
            ) : null}

            {streamorder > 0 ? (
              <Entry>
                <Text>Stream order (NHD modified Strahler): {streamorder}</Text>
              </Entry>
            ) : null}

            {streamsizeclass ? (
              <Entry>
                <Text>
                  Stream size class: {STREAM_SIZECLASS[streamsizeclass]}
                  <br />
                  (drainage area:{' '}
                  {STREAM_SIZECLASS_DRAINAGE_AREA[streamsizeclass]} km2)
                </Text>
              </Entry>
            ) : null}

            {hasLandOwner ? (
              <Entry>
                <Text>Conservation land type: {OWNERTYPE[ownertype]}</Text>
              </Entry>
            ) : null}

            {hasBarrierOwner ? (
              <Entry>
                <Text>
                  Barrier ownership type: {BARRIEROWNERTYPE[barrierownertype]}
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
          <>
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

                {/* Have to evalute nostructure on each or Entries doesn't work */}
                {!nostructure && height > 0 ? (
                  <Entry>
                    <Text>Height: {height} feet</Text>
                  </Entry>
                ) : null}

                {!nostructure && width > 0 ? (
                  <Entry>
                    <Text>Width: {width} feet</Text>
                  </Entry>
                ) : null}

                {!nostructure && construction !== null && construction >= 0 ? (
                  <Entry>
                    <Text>
                      Construction material:{' '}
                      {CONSTRUCTION[construction].toLowerCase()}
                    </Text>
                  </Entry>
                ) : null}

                {!nostructure && condition !== null && condition >= 0 ? (
                  <Entry>
                    <Text>
                      Structural condition: {CONDITION[condition].toLowerCase()}
                    </Text>
                  </Entry>
                ) : null}

                {!nostructure &&
                passagefacility !== null &&
                passagefacility >= 0 ? (
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
                    <Text>Condition: {condition}</Text>
                  </Entry>
                ) : null}

                {barrierseverity !== null && barrierseverity >= 0 ? (
                  <Entry>
                    <Text>Severity: {BARRIER_SEVERITY[barrierseverity]}</Text>
                  </Entry>
                ) : null}

                {sarp_score >= 0 ? (
                  <Entry>
                    <Text>
                      SARP Aquatic Organism Passage Score:{' '}
                      {formatNumber(sarp_score, 1)} (
                      {classifySARPScore(sarp_score)})
                    </Text>
                  </Entry>
                ) : null}
              </Entries>
            )}
          </>
        </View>
      </Flex>
    </Section>
  )
}

Location.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  height: PropTypes.number,
  width: PropTypes.number,
  yearcompleted: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passagefacility: PropTypes.number,
  estimated: PropTypes.bool,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  constriction: PropTypes.number,
  barrierseverity: PropTypes.number,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  huc12: PropTypes.string,
  subwatershed: PropTypes.string,
  subbasin: PropTypes.string,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  sarp_score: PropTypes.number,
  diversion: PropTypes.number,
  lowheaddam: PropTypes.number,
  nostructure: PropTypes.bool,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  invasive: PropTypes.bool,
}

Location.defaultProps = {
  height: 0,
  width: 0,
  yearcompleted: 0,
  construction: 0,
  purpose: null,
  condition: null,
  passagefacility: null,
  estimated: false,
  roadtype: null,
  crossingtype: null,
  constriction: null,
  barrierseverity: null,
  river: null,
  intermittent: 0,
  huc12: null,
  subwatershed: null,
  subbasin: null,
  ownertype: null,
  barrierownertype: null,
  sarp_score: -1,
  diversion: 0,
  lowheaddam: null,
  nostructure: false,
  streamorder: 0,
  streamsizeclass: null,
  waterbodykm2: -1,
  waterbodysizeclass: null,
  invasive: false,
}

export default Location
