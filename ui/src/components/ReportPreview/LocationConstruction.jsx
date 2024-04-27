import React from 'react'
import PropTypes from 'prop-types'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { Box, Flex, Grid, Heading, Text } from 'theme-ui'

import { classifySARPScore } from 'components/BarrierDetails/SmallBarrierDetails'
import {
  siteMetadata,
  barrierTypeLabelSingular,
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
  FISH_HABITAT_PARTNERSHIP,
  STATE_REGULATED,
  WATER_RIGHT,
  DISADVANTAGED_COMMUNITY,
  PURPOSE,
  PASSABILITY,
  SMALL_BARRIER_SEVERITY,
  STREAM_SIZECLASS,
  STREAM_SIZECLASS_DRAINAGE_AREA,
  WATERBODY_SIZECLASS,
} from 'config'
import { OutboundLink } from 'components/Link'
import { formatNumber } from 'util/format'
import { Entry } from './elements'

const { version: dataVersion } = siteMetadata

const LocationConstruction = ({
  barrierType,
  sarpid,
  river,
  intermittent,
  subbasin,
  subwatershed,
  huc12,
  ownertype,
  barrierownertype,
  fercregulated,
  stateregulated,
  fedregulatoryagency,
  waterright,
  disadvantagedcommunity,
  hazard,
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
  passability,
  barrierseverity,
  sarp_score,
  diversion,
  streamorder,
  streamsizeclass,
  waterbodykm2,
  waterbodysizeclass,
  invasive,
  removed,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  nativeterritories,
  sx,
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
    <Box sx={sx}>
      <Heading as="h3">Location & construction information</Heading>

      <Grid columns={2} gap={0}>
        <Box sx={{ mr: '1rem' }}>
          <Entry>
            <>
              Barrier Type:{' '}
              {isLowheadDam ? (
                <>
                  {lowheaddam === 2 ? 'likely ' : null}
                  lowhead dam
                </>
              ) : null}
              {isDiversion ? (
                <>
                  {isLowheadDam ? (
                    <>
                      ,<br />
                    </>
                  ) : null}{' '}
                  {diversion === 2 ? 'likely ' : null} water diversion
                </>
              ) : null}
              {!(isLowheadDam || isDiversion) ? barrierTypeLabel : null}
              {invasive ? (
                <>
                  ,<br /> invasive species barrier
                </>
              ) : null}
            </>

            {estimated ? (
              <Flex sx={{ alignItems: 'flex-start', mt: '0.5rem' }}>
                <Box sx={{ color: 'grey.4', flex: '0 0 auto', mr: '0.5em' }}>
                  <ExclamationTriangle size="2em" />
                </Box>
                <Text sx={{ flex: '1 1 auto', lineHeight: 1.1, fontSize: 1 }}>
                  Dam is estimated from other data sources and may be incorrect;
                  please{' '}
                  <a
                    href={`mailto:Kat@southeastaquatics.net?subject=Problem with Estimated Dam ${sarpid} (data version: ${dataVersion})`}
                  >
                    let us know
                  </a>
                </Text>
              </Flex>
            ) : null}
          </Entry>
          <Entry>
            {hasRiver ? `On ${river} in` : 'Within'} {subwatershed}{' '}
            Subwatershed, {subbasin} Subbasin
            <br />
            HUC12: {huc12}
          </Entry>

          {intermittent ? (
            <Entry>
              This {barrierTypeLabel} on a reach that has intermittent or
              ephemeral flow
            </Entry>
          ) : null}

          {barrierType === 'dams' &&
          waterbodysizeclass !== null &&
          waterbodysizeclass > 0 ? (
            <Entry>
              This {barrierTypeLabel} is associated with a{' '}
              {WATERBODY_SIZECLASS[waterbodysizeclass]
                .split(' (')[0]
                .toLowerCase()}{' '}
              (
              {waterbodykm2 > 0.1
                ? `${formatNumber(waterbodykm2, 2)} k`
                : `${formatNumber(waterbodykm2 * 1e6)} `}
              m<sup>2</sup>).
            </Entry>
          ) : null}

          {streamorder > 0 ? (
            <Entry>Stream order (NHD modified Strahler): {streamorder}</Entry>
          ) : null}

          {streamsizeclass ? (
            <Entry>
              Stream size class: {STREAM_SIZECLASS[streamsizeclass]}
              <br />
              (drainage area: {
                STREAM_SIZECLASS_DRAINAGE_AREA[streamsizeclass]
              }{' '}
              km
              <sup>2</sup>)
            </Entry>
          ) : null}

          {hasLandOwner ? (
            <Entry>Conservation land type: {OWNERTYPE[ownertype]}</Entry>
          ) : null}

          {barrierownertype !== null ? (
            <Entry>
              Barrier ownership type: {BARRIEROWNERTYPE[barrierownertype]}
            </Entry>
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

          {disadvantagedcommunity ? (
            <Entry>
              Climate and environmental justice:{' '}
              {disadvantagedcommunity
                .split(',')
                .map((type) => DISADVANTAGED_COMMUNITY[type].toLowerCase())
                .join(', ')}
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
                  SARP Aquatic Organism Passage Score:{' '}
                  {formatNumber(sarp_score, 1)} ({classifySARPScore(sarp_score)}
                  )
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

          {ejtract || ejtribal ? (
            <Entry>
              Climate and environmental justice:{' '}
              {ejtract ? 'within a disadvantaged census tract' : null}
              {ejtract && ejtribal ? ', ' : null}
              {ejtribal ? 'within a tribal community' : null}
            </Entry>
          ) : null}

          {nativeterritories ? (
            <Entry>
              <Text>Within the following native territories:</Text>
              <Text sx={{ fontSize: 1, mt: '0.5rem' }}>
                {nativeterritories}
              </Text>
              <Text sx={{ fontSize: 0, color: 'grey.7' }}>
                (based on data provided by{' '}
                <OutboundLink to="https://native-land.ca/">
                  Native Land Digital
                </OutboundLink>
                )
              </Text>
            </Entry>
          ) : null}
        </Box>
      </Grid>

      {fishhabitatpartnership ? (
        <Box sx={{ mt: '3rem' }}>
          <Text>Fish Habitat Partnerships working in this area:</Text>
          <Text sx={{ mt: '0.25rem', ml: '1rem' }}>
            {fishhabitatpartnership.split(',').map((code, i) => (
              <>
                {i > 0 ? ', ' : null}
                <OutboundLink to={FISH_HABITAT_PARTNERSHIP[code].url}>
                  {FISH_HABITAT_PARTNERSHIP[code].name}
                </OutboundLink>
              </>
            ))}
          </Text>
        </Box>
      ) : null}
    </Box>
  )
}

LocationConstruction.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  subbasin: PropTypes.string,
  subwatershed: PropTypes.string,
  huc12: PropTypes.string,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  fercregulated: PropTypes.number,
  stateregulated: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  waterright: PropTypes.number,
  disadvantagedcommunity: PropTypes.string,
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
  sarp_score: PropTypes.number,
  diversion: PropTypes.number,
  lowheaddam: PropTypes.number,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  invasive: PropTypes.bool,
  removed: PropTypes.bool,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  fishhabitatpartnership: PropTypes.string,
  nativeterritories: PropTypes.string,
  sx: PropTypes.object,
}

LocationConstruction.defaultProps = {
  river: null,
  intermittent: 0,
  subbasin: null,
  subwatershed: null,
  huc12: null,
  ownertype: null,
  barrierownertype: null,
  fercregulated: null,
  stateregulated: null,
  fedregulatoryagency: null,
  waterright: null,
  disadvantagedcommunity: null,
  height: 0,
  width: 0,
  hazard: null,
  yearcompleted: 0,
  construction: null,
  purpose: null,
  condition: null,
  passagefacility: null,
  estimated: false,
  roadtype: null,
  crossingtype: null,
  constriction: null,
  passability: null,
  barrierseverity: null,
  sarp_score: -1,
  diversion: 0,
  lowheaddam: null,
  streamorder: 0,
  streamsizeclass: null,
  waterbodykm2: -1,
  waterbodysizeclass: null,
  invasive: false,
  removed: false,
  ejtract: false,
  ejtribal: false,
  fishhabitatpartnership: null,
  nativeterritories: null,
  sx: null,
}

export default LocationConstruction
