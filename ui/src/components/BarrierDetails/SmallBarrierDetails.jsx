import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import {
  SMALL_BARRIER_SEVERITY,
  CONDITION,
  CROSSING_TYPE,
  ROAD_TYPE,
  CONSTRICTION,
  PASSAGEFACILITY,
} from 'config'

import DiadromousInfo from './DiadromousInfo'
import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NetworkInfo from './NetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesInfo from './SpeciesInfo'

export const classifySARPScore = (score) => {
  // assumes -1 (NODATA) already filtered out
  if (score < 0.2) {
    return 'severe barrier'
  }
  if (score < 0.4) {
    return 'significant barrier'
  }
  if (score < 0.6) {
    return 'moderate barrier'
  }
  if (score < 0.8) {
    return 'minor barrier'
  }
  if (score < 1) {
    return 'insignificant barrier'
  }
  if (score >= 1) {
    return 'no barrier'
  }
  return 'not calculated'
}

const BarrierDetails = ({
  barrierType,
  networkType,
  sarpid,

  alteredupstreammiles,
  barrierownertype,
  barrierseverity,
  basin,
  condition,
  constriction,
  crossingtype,
  ejtract,
  ejtribal,
  excluded,
  flowstoocean,
  freealtereddownstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freeunaltereddownstreammiles,
  hasnetwork,
  huc12,
  in_network_type,
  intermittent,
  invasive,
  landcover,
  link,
  milestooutlet,
  nearestcrossingid,
  onloop,
  ownertype,
  passagefacility,
  perennialupstreammiles,
  regionalsgcnspp,
  removed,
  road,
  roadtype,
  salmonidesu,
  sarp_score,
  sizeclasses,
  snapped,
  source,
  statesgcnspp,
  stream,
  streamorder,
  streamsizeclass,
  subwatershed,
  tespp,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  totalupstreammiles,
  trout,
  unalteredupstreammiles,
  unranked,
  waterbodykm2,
  waterbodysizeclass,
  yearremoved,
}) => (
  <Box
    sx={{
      mt: '-1rem',
      mx: '-0.5rem',
      fontSize: 1,
    }}
  >
    <Section title="Location">
      <Entry>
        <Field label="Barrier type">
          Road-related <br />
          potential barrier
          {invasive ? (
            <>
              ,<br />
              invasive species barrier
            </>
          ) : null}
          {removed ? (
            <>
              <br />
              {yearremoved !== null && yearremoved > 0
                ? `(removed in ${yearremoved})`
                : '(removed)'}
            </>
          ) : null}
        </Field>
      </Entry>
      {!isEmptyString(road) ? (
        <Entry>
          <Field label="Road">{road}</Field>
        </Entry>
      ) : null}

      <LocationInfo
        barrierType={barrierType}
        reachName={stream}
        basin={basin}
        subwatershed={subwatershed}
        huc12={huc12}
        ownertype={ownertype}
        barrierownertype={barrierownertype}
        ejtract={ejtract}
        ejtribal={ejtribal}
        intermittent={intermittent}
        streamorder={streamorder}
        streamsizeclass={streamsizeclass}
        waterbodysizeclass={waterbodysizeclass}
        waterbodykm2={waterbodykm2}
      />
    </Section>

    <Section title="Barrier information">
      {roadtype !== null && roadtype >= 0 ? (
        <Entry>
          <Field label="Road type" isUnknown={roadtype === 0}>
            {ROAD_TYPE[roadtype]}
          </Field>
        </Entry>
      ) : null}
      {crossingtype !== null && crossingtype >= 0 ? (
        <Entry>
          <Field label="Crossing type" isUnknown={crossingtype === 0}>
            {CROSSING_TYPE[crossingtype]}
          </Field>
        </Entry>
      ) : null}
      {condition !== null && condition >= 0 ? (
        <Entry>
          <Field label="Condition" isUnknown={condition === 0}>
            {CONDITION[condition]}
          </Field>
        </Entry>
      ) : null}
      {constriction !== null && constriction >= 0 ? (
        <Entry>
          <Field label="Type of constriction" isUnknown={constriction === 0}>
            {CONSTRICTION[constriction]}
          </Field>
        </Entry>
      ) : null}
      {barrierseverity !== null ? (
        <Entry>
          <Field label="Severity" isUnknown={barrierseverity === 0}>
            {SMALL_BARRIER_SEVERITY[barrierseverity]}
          </Field>
        </Entry>
      ) : null}
      {sarp_score >= 0 ? (
        <Entry>
          <Field label="SARP Aquatic Organism Passage score">
            {formatNumber(sarp_score, 1)}
            <Text sx={{ fontSize: 0, color: 'grey.8' }}>
              ({classifySARPScore(sarp_score)})
            </Text>
          </Field>
        </Entry>
      ) : null}
      {passagefacility !== null &&
      passagefacility >= 0 &&
      PASSAGEFACILITY[passagefacility] ? (
        <Entry>
          <Field
            label="Passage facility type"
            isUnknown={passagefacility === 0}
          >
            {PASSAGEFACILITY[passagefacility].toLowerCase()}
          </Field>
        </Entry>
      ) : null}
    </Section>

    <Section title="Functional network information">
      {removed ? (
        <Entry sx={{ mb: '1rem' }}>
          {yearremoved !== null && yearremoved > 0
            ? `This barrier was removed or mitigated in ${yearremoved}.`
            : 'This barrier has been removed or mitigated.'}
        </Entry>
      ) : null}

      {hasnetwork ? (
        <NetworkInfo
          barrierType={barrierType}
          networkType={networkType}
          totalupstreammiles={totalupstreammiles}
          perennialupstreammiles={perennialupstreammiles}
          alteredupstreammiles={alteredupstreammiles}
          unalteredupstreammiles={unalteredupstreammiles}
          freedownstreammiles={freedownstreammiles}
          freeperennialdownstreammiles={freeperennialdownstreammiles}
          freealtereddownstreammiles={freealtereddownstreammiles}
          freeunaltereddownstreammiles={freeunaltereddownstreammiles}
          sizeclasses={sizeclasses}
          landcover={landcover}
          intermittent={intermittent}
          invasive={invasive}
          unranked={unranked}
          removed={removed}
        />
      ) : (
        <NoNetworkInfo
          barrierType={barrierType}
          networkType={networkType}
          snapped={snapped}
          excluded={excluded}
          in_network_type={in_network_type}
          onloop={onloop}
        />
      )}
    </Section>

    {hasnetwork && flowstoocean && milestooutlet < 500 ? (
      <Section title="Diadromous species information">
        <DiadromousInfo
          barrierType={barrierType}
          milestooutlet={milestooutlet}
          totaldownstreamdams={totaldownstreamdams}
          totaldownstreamsmallbarriers={totaldownstreamsmallbarriers}
          totaldownstreamwaterfalls={totaldownstreamwaterfalls}
        />
      </Section>
    ) : null}

    <Section title="Species information for this subwatershed">
      <SpeciesInfo
        barrierType={barrierType}
        tespp={tespp}
        regionalsgcnspp={regionalsgcnspp}
        statesgcnspp={statesgcnspp}
        trout={trout}
        salmonidesu={salmonidesu}
      />
    </Section>

    <Section title="Other information">
      <IDInfo
        sarpid={sarpid}
        source={source}
        link={link}
        nearestcrossingid={nearestcrossingid}
      />
    </Section>
  </Box>
)

BarrierDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,

  alteredupstreammiles: PropTypes.number,
  barrierownertype: PropTypes.number,
  barrierseverity: PropTypes.number,
  basin: PropTypes.string,
  condition: PropTypes.number,
  constriction: PropTypes.number,
  crossingtype: PropTypes.number,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  excluded: PropTypes.bool,
  flowstoocean: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  hasnetwork: PropTypes.bool.isRequired,
  huc12: PropTypes.string,
  in_network_type: PropTypes.bool,
  intermittent: PropTypes.number,
  invasive: PropTypes.bool,
  landcover: PropTypes.number,
  link: PropTypes.string,
  milestooutlet: PropTypes.number,
  nearestcrossingid: PropTypes.string,
  onloop: PropTypes.bool,
  ownertype: PropTypes.number,
  passagefacility: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  removed: PropTypes.bool,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  salmonidesu: PropTypes.string,
  sarp_score: PropTypes.number,
  sizeclasses: PropTypes.number,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  statesgcnspp: PropTypes.number,
  stream: PropTypes.string,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  subwatershed: PropTypes.string,
  tespp: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
  totalupstreammiles: PropTypes.number,
  trout: PropTypes.number,
  unalteredupstreammiles: PropTypes.number,
  unranked: PropTypes.bool,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  yearremoved: PropTypes.number,
}

BarrierDetails.defaultProps = {
  alteredupstreammiles: 0,
  barrierownertype: null,
  barrierseverity: null,
  basin: null,
  condition: null,
  constriction: null,
  crossingtype: null,
  ejtract: false,
  ejtribal: false,
  excluded: false,
  flowstoocean: 0,
  freealtereddownstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  huc12: null,
  in_network_type: false,
  intermittent: -1,
  invasive: 0,
  landcover: null,
  link: null,
  milestooutlet: 0,
  nearestcrossingid: null,
  onloop: false,
  ownertype: null,
  passagefacility: null,
  perennialupstreammiles: 0,
  regionalsgcnspp: 0,
  removed: false,
  road: null,
  roadtype: null,
  salmonidesu: null,
  sarp_score: -1,
  sizeclasses: null,
  snapped: false,
  source: null,
  statesgcnspp: 0,
  stream: null,
  streamorder: 0,
  streamsizeclass: null,
  subwatershed: null,
  tespp: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
  totalupstreammiles: 0,
  trout: 0,
  unalteredupstreammiles: 0,
  unranked: false,
  waterbodykm2: -1,
  waterbodysizeclass: null,
  yearremoved: 0,
}

export default BarrierDetails
