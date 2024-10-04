import React from 'react'
import PropTypes from 'prop-types'
import { Text, View, Svg, Path, Link } from '@react-pdf/renderer'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import {
  siteMetadata,
  barrierTypeLabelSingular,
  HAZARD,
  CONDITION,
  CONSTRUCTION,
  CONSTRICTION,
  CROSSING_TYPE,
  ROAD_TYPE,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  FERC_REGULATED,
  FISH_HABITAT_PARTNERSHIPS,
  STATE_REGULATED,
  WATER_RIGHT,
  PASSAGEFACILITY,
  PURPOSE,
  PASSABILITY,
  SMALL_BARRIER_SEVERITY,
  STATES,
  STREAM_SIZECLASS,
  STREAM_SIZECLASS_DRAINAGE_AREA,
  WATERBODY_SIZECLASS,
} from 'config'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import { Flex, Entry, Entries, Section } from './elements'

const { version: dataVersion } = siteMetadata

const Location = ({
  barrierType,
  sarpid,
  annualflow,
  hazard,
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
  passability,
  barrierseverity,
  river,
  intermittent,
  subwatershed,
  subbasin,
  huc12,
  congressionaldistrict,
  ownertype,
  barrierownertype,
  fercregulated,
  stateregulated,
  fedregulatoryagency,
  waterright,
  disadvantagedcommunity,
  sarp_score,
  diversion,
  streamorder,
  streamsizeclass,
  storagevolume,
  waterbodyacres,
  waterbodysizeclass,
  invasive,
  removed,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  nativeterritories,
  costlower,
  costmean,
  costupper,
  fatality,
  protocolused,
  wildscenicriver,
  ...props
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]

  const hasRiver =
    river &&
    river !== '"' &&
    river !== 'null' &&
    river.toLowerCase() !== 'unknown' &&
    river.toLowerCase() !== 'unnamed'

  const hasLandOwner = ownertype && ownertype > 0
  const isLowheadDam = lowheaddam === 1 || lowheaddam === 2
  const isDiversion = diversion !== null && diversion >= 1

  return (
    <Section
      title="Location & construction information"
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
            <Entry>
              <Text>
                Barrier Type:{' '}
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
                  </>
                ) : null}
                {!(isLowheadDam || isDiversion) ? (
                  <> {barrierTypeLabel}</>
                ) : null}
                {invasive ? ', invasive species barrier' : null}
              </Text>

              {estimated ? (
                <Flex style={{ alignItems: 'flex-start', marginTop: '6pt' }}>
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
                      fontSize: '11pt',
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
              ) : null}
            </Entry>

            <Entry>
              <Text>
                {hasRiver ? `On ${river} in` : 'Within'} {subwatershed}{' '}
                Subwatershed, {subbasin} Subbasin
              </Text>
              <Text>HUC12: {huc12}</Text>
            </Entry>

            {wildscenicriver ? (
              <Entry>
                <Text>
                  Near{' '}
                  {wildscenicriver
                    .split(', ')
                    .map((name) => `${name} Wild & Scenic River`)
                    .join(', ')}
                </Text>
                <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                  (within 250 meters)
                </Text>
              </Entry>
            ) : null}

            {intermittent ? (
              <Entry>
                <Text>
                  This {barrierTypeLabel} is located on a reach that has
                  intermittent or ephemeral flow
                </Text>
              </Entry>
            ) : null}

            {storagevolume !== null ? (
              <Entry>
                <Text>
                  Normal storage volume: {formatNumber(storagevolume)} acre/feet
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
                  {formatNumber(waterbodyacres)} acres.
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
                </Text>
                <Text>
                  (drainage area:{' '}
                  {STREAM_SIZECLASS_DRAINAGE_AREA[streamsizeclass]})
                </Text>
              </Entry>
            ) : null}

            {annualflow !== null && annualflow >= 0 ? (
              <Entry>
                <Text>
                  Stream reach annual flow rate: {formatNumber(annualflow)} CFS
                </Text>
              </Entry>
            ) : null}

            {hasLandOwner ? (
              <Entry>
                <Text>Conservation land type: {OWNERTYPE[ownertype]}</Text>
              </Entry>
            ) : null}

            {barrierownertype !== null ? (
              <Entry>
                <Text>
                  Barrier ownership type:{' '}
                  {BARRIEROWNERTYPE[barrierownertype].toLowerCase()}
                </Text>
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

              {ejtract || ejtribal ? (
                <Entry>
                  <Text>
                    Climate and environmental justice:{' '}
                    {ejtract ? 'within a disadvantaged census tract' : null}
                    {ejtract && ejtribal ? ', ' : null}
                    {ejtribal ? 'within a tribal community' : null}
                  </Text>
                </Entry>
              ) : null}

              {nativeterritories ? (
                <Entry>
                  <Text>Within the following native territories:</Text>
                  <Text
                    style={{
                      fontSize: '12pt',
                      marginTop: '6pt',
                    }}
                  >
                    {nativeterritories}
                  </Text>
                  <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                    (based on data provided by{' '}
                    <Link href="https://native-land.ca/">
                      Native Land Digital
                    </Link>
                    )
                  </Text>
                </Entry>
              ) : null}

              {congressionaldistrict ? (
                <Entry>
                  <Text>
                    Congressional district:{' '}
                    {STATES[congressionaldistrict.slice(0, 2)]} Congressional
                    District {congressionaldistrict.slice(2)}
                  </Text>
                  <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                    (118th congress)
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
              {ejtract || ejtribal ? (
                <Entry>
                  <Text>
                    Climate and environmental justice:{' '}
                    {ejtract ? 'within a disadvantaged census tract' : null}
                    {ejtract && ejtribal ? ', ' : null}
                    {ejtribal ? 'within a tribal community' : null}
                  </Text>
                </Entry>
              ) : null}

              {nativeterritories ? (
                <Entry>
                  <Text>Within the following native territories:</Text>
                  <Text style={{ marginTop: '6pt' }}>{nativeterritories}</Text>
                  <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                    Note: fonts for native territories may not render properly;
                    our apologies, no disrespect is intended.
                  </Text>
                  <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                    (based on data provided by{' '}
                    <Link href="https://native-land.ca/">
                      Native Land Digital
                    </Link>
                    )
                  </Text>
                </Entry>
              ) : null}

              {congressionaldistrict ? (
                <Entry>
                  <Text>
                    Congressional district:{' '}
                    {STATES[congressionaldistrict.slice(0, 2)]} Congressional
                    District {congressionaldistrict.slice(2)}
                  </Text>
                  <Text style={{ fontSize: '10pt', color: '#7f8a93' }}>
                    (118th congress)
                  </Text>
                </Entry>
              ) : null}
            </Entries>
          )}
        </View>
      </Flex>

      {fishhabitatpartnership ? (
        <View style={{ marginTop: '20pt' }}>
          <Text>Fish Habitat Partnerships working in this area:</Text>
          <Text sx={{ mt: '0.25rem', ml: '1rem' }}>
            {fishhabitatpartnership.split(',').map((code, i) => (
              <React.Fragment key={code}>
                {i > 0 ? ', ' : null}
                <Link href={FISH_HABITAT_PARTNERSHIPS[code].url}>
                  {FISH_HABITAT_PARTNERSHIPS[code].name}
                </Link>
              </React.Fragment>
            ))}
          </Text>
        </View>
      ) : null}
    </Section>
  )
}

Location.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  annualflow: PropTypes.number,
  height: PropTypes.number,
  width: PropTypes.number,
  yearcompleted: PropTypes.number,
  hazard: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passagefacility: PropTypes.number,
  estimated: PropTypes.bool,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  constriction: PropTypes.number,
  passability: PropTypes.number,
  barrierseverity: PropTypes.number,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  huc12: PropTypes.string,
  congressionaldistrict: PropTypes.string,
  subwatershed: PropTypes.string,
  subbasin: PropTypes.string,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  fercregulated: PropTypes.number,
  stateregulated: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  waterright: PropTypes.number,
  disadvantagedcommunity: PropTypes.string,
  sarp_score: PropTypes.number,
  diversion: PropTypes.number,
  lowheaddam: PropTypes.number,
  storagevolume: PropTypes.number,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodyacres: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  invasive: PropTypes.bool,
  removed: PropTypes.bool,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  fishhabitatpartnership: PropTypes.string,
  nativeterritories: PropTypes.string,
  costlower: PropTypes.number,
  costmean: PropTypes.number,
  costupper: PropTypes.number,
  fatality: PropTypes.number,
  protocolused: PropTypes.string,
  wildscenicriver: PropTypes.string,
}

Location.defaultProps = {
  annualflow: null,
  height: 0,
  width: 0,
  yearcompleted: 0,
  hazard: null,
  construction: 0,
  purpose: null,
  condition: null,
  passagefacility: null,
  estimated: false,
  roadtype: null,
  crossingtype: null,
  constriction: null,
  passability: null,
  barrierseverity: null,
  river: null,
  intermittent: 0,
  huc12: null,
  congressionaldistrict: null,
  subwatershed: null,
  subbasin: null,
  ownertype: null,
  barrierownertype: null,
  fercregulated: null,
  stateregulated: null,
  fedregulatoryagency: null,
  waterright: null,
  disadvantagedcommunity: null,
  sarp_score: -1,
  diversion: 0,
  lowheaddam: null,
  storagevolume: null,
  streamorder: 0,
  streamsizeclass: null,
  waterbodyacres: -1,
  waterbodysizeclass: null,
  invasive: false,
  removed: false,
  ejtract: false,
  ejtribal: false,
  fishhabitatpartnership: null,
  nativeterritories: null,
  costlower: 0,
  costmean: 0,
  costupper: 0,
  fatality: 0,
  protocolused: null,
  wildscenicriver: null,
}

export default Location
