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
  source,
  link,
  hasnetwork,
  excluded,
  in_network_type,
  onloop,
  snapped,
  stream,
  intermittent,
  huc12,
  basin,
  subwatershed,
  road,
  roadtype,
  crossingtype,
  constriction,
  condition,
  passagefacility,
  sarp_score,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  ownertype,
  barrierownertype,
  disadvantagedcommunity,
  barrierseverity,
  removed,
  yearremoved,
  invasive,
  unranked,
  streamorder,
  streamsizeclass,
  waterbodysizeclass,
  waterbodykm2,
  // metrics
  totalupstreammiles,
  perennialupstreammiles,
  alteredupstreammiles,
  unalteredupstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freealtereddownstreammiles,
  freeunaltereddownstreammiles,
  landcover,
  sizeclasses,
  flowstoocean,
  milestooutlet,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
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
        disadvantagedcommunity={disadvantagedcommunity}
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
      <IDInfo sarpid={sarpid} source={source} link={link} />
    </Section>
  </Box>
)

BarrierDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  onloop: PropTypes.bool,
  snapped: PropTypes.bool,
  excluded: PropTypes.bool,
  in_network_type: PropTypes.bool,
  source: PropTypes.string,
  link: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
  huc12: PropTypes.string,
  basin: PropTypes.string,
  subwatershed: PropTypes.string,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  constriction: PropTypes.number,
  condition: PropTypes.number,
  barrierseverity: PropTypes.number,
  passagefacility: PropTypes.number,
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  disadvantagedcommunity: PropTypes.string,
  totalupstreammiles: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  alteredupstreammiles: PropTypes.number,
  unalteredupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
  sarp_score: PropTypes.number,
  invasive: PropTypes.bool,
  unranked: PropTypes.bool,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  flowstoocean: PropTypes.number,
  milestooutlet: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
}

BarrierDetails.defaultProps = {
  huc12: null,
  basin: null,
  subwatershed: null,
  excluded: false,
  in_network_type: false,
  onloop: false,
  snapped: false,
  source: null,
  link: null,
  stream: null,
  intermittent: -1,
  road: null,
  roadtype: null,
  crossingtype: null,
  constriction: null,
  barrierseverity: null,
  passagefacility: null,
  removed: false,
  yearremoved: 0,
  condition: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
  ownertype: null,
  barrierownertype: null,
  disadvantagedcommunity: null,
  totalupstreammiles: 0,
  perennialupstreammiles: 0,
  alteredupstreammiles: 0,
  unalteredupstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freealtereddownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  landcover: null,
  sizeclasses: null,
  sarp_score: -1,
  invasive: 0,
  unranked: false,
  streamorder: 0,
  streamsizeclass: null,
  waterbodykm2: -1,
  waterbodysizeclass: null,
  flowstoocean: 0,
  milestooutlet: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
}

export default BarrierDetails
