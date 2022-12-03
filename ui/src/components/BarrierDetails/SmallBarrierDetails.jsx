import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph, Text } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import {
  BARRIER_SEVERITY,
  CONDITION,
  CROSSING_TYPE,
  ROAD_TYPE,
  CONSTRICTION,
  OWNERTYPE,
  BARRIEROWNERTYPE,
  SALMONID_ESU,
} from 'config'

import NetworkInfo from './NetworkInfo'

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
  sarpid,
  lat,
  lon,
  source,
  hasnetwork,
  excluded,
  stream,
  intermittent,
  HUC8,
  HUC12,
  HUC8Name,
  HUC12Name,
  road,
  roadtype,
  crossingtype,
  constriction,
  condition,
  sarp_score,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  ownertype,
  barrierownertype,
  barrierseverity,
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
}) => {
  const isCrossing = sarpid.startsWith('cr')

  return (
    <Box
      sx={{
        mt: '-1rem',
        mx: '-1rem',
        fontSize: 1,
      }}
    >
      <Section title="Location">
        <Entry>
          {isCrossing
            ? 'Road / stream crossing'
            : 'Road-related potential barrier'}{' '}
          at {formatNumber(lat, 5)}
          &deg; N, {formatNumber(lon, 5)}
          &deg; E
        </Entry>
        {!isEmptyString(stream) ? (
          <Entry>
            <Field>River or stream:</Field> {stream}
          </Entry>
        ) : null}
        {!isEmptyString(road) ? (
          <Entry>
            <Field>Road:</Field> {road}
          </Entry>
        ) : null}

        {intermittent === 1 ? (
          <Entry>
            Located on a reach that has intermittent or ephemeral flow
          </Entry>
        ) : null}

        {HUC12Name ? (
          <Entry>
            {HUC12Name} Subwatershed{' '}
            <Paragraph variant="help" sx={{ fontSize: 0 }}>
              HUC12: {HUC12}
            </Paragraph>
          </Entry>
        ) : null}

        {HUC8Name ? (
          <Entry>
            {HUC8Name} Subbasin{' '}
            <Paragraph variant="help" sx={{ fontSize: 0 }}>
              HUC8: {HUC8}
            </Paragraph>
          </Entry>
        ) : null}

        {ownertype !== null && ownertype > 0 ? (
          <Entry>
            <Field>Conservation land type:</Field> {OWNERTYPE[ownertype]}
          </Entry>
        ) : null}

        {barrierownertype !== null && barrierownertype > 0 ? (
          <Entry>
            <Field>Barrier ownership type:</Field>{' '}
            {BARRIEROWNERTYPE[barrierownertype]}
          </Entry>
        ) : null}
      </Section>

      <Section title="Barrier information">
        {roadtype !== null && roadtype >= 0 ? (
          <Entry>
            <Field>Road type:</Field> {ROAD_TYPE[roadtype]}
          </Entry>
        ) : null}
        {crossingtype !== null && crossingtype >= 0 ? (
          <Entry>
            <Field>Crossing type:</Field> {CROSSING_TYPE[crossingtype]}
          </Entry>
        ) : null}
        {condition !== null && condition >= 0 ? (
          <Entry>
            <Field>Condition:</Field> {CONDITION[condition]}
          </Entry>
        ) : null}
        {constriction !== null && constriction >= 0 ? (
          <Entry>
            <Field>Type of constriction:</Field> {CONSTRICTION[constriction]}
          </Entry>
        ) : null}
        {barrierseverity !== null ? (
          <Entry>
            <Field>Severity:</Field> {BARRIER_SEVERITY[barrierseverity]}
          </Entry>
        ) : null}
        {!isCrossing && sarp_score >= 0 ? (
          <Entry>
            <Field>SARP Aquatic Organism Passage Score:</Field>{' '}
            {formatNumber(sarp_score, 1)} ({classifySARPScore(sarp_score)})
          </Entry>
        ) : null}
      </Section>

      <Section title="Functional network information">
        {hasnetwork ? (
          <NetworkInfo
            barrierType={barrierType}
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
          />
        ) : (
          <>
            {excluded ? (
              <Entry>
                This road-related barrier was excluded from the connectivity
                analysis based on field reconnaissance or manual review of
                aerial imagery.
              </Entry>
            ) : (
              <>
                {isCrossing ? (
                  <Entry>
                    This crossing has not yet been evaluated for aquatic
                    connectivity.
                  </Entry>
                ) : (
                  <Entry>
                    <Text>
                      This barrier is off-network and has no functional network
                      information.
                    </Text>
                    <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
                      Not all barriers could be correctly snapped to the aquatic
                      network for analysis. Please contact us to report an error
                      or for assistance interpreting these results.
                    </Paragraph>
                  </Entry>
                )}
              </>
            )}
          </>
        )}
      </Section>

      <Section title="Species information">
        {tespp + regionalsgcnspp > 0 || trout || salmonidesu ? (
          <>
            <Text sx={{ my: '0.5rem', mr: '0.5rem' }}>
              Data sources in the subwatershed containing this barrier have
              recorded:
            </Text>
            <Box as="ul">
              <li>
                <b>{tespp}</b> federally-listed threatened and endangered
                aquatic species
              </li>
              <li>
                <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
                Conservation Need (SGCN), which include state-listed threatened
                and endangered species
              </li>
              <li>
                <b>{regionalsgcnspp}</b> regionally-listed aquatic Species of
                Greatest Conservation Need
              </li>
              <li>
                {trout ? 'One or more trout species' : 'No trout species'}
              </li>
              {salmonidesu ? (
                <li>
                  Within{' '}
                  {salmonidesu
                    .split(',')
                    .map((code) => SALMONID_ESU[code])
                    .join(', ')}
                </li>
              ) : null}
            </Box>
          </>
        ) : (
          <Text sx={{ my: '0.5rem', mr: '0.5rem', color: 'grey.8' }}>
            Data sources in the subwatershed containing this dam have not
            recorded any federally-listed threatened and endangered aquatic
            species, state-listed aquatic Species of Greatest Conservation Need,
            regionally-listed aquatic Species of Greatest Conservation Need,
            trout species, or salmon ESU / steelhead trout DPS.
          </Text>
        )}

        <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
          Note: species information is very incomplete. These species may or may
          not be directly impacted by this barrier.{' '}
          <a href="/sgcn" target="_blank">
            Read more.
          </a>
        </Paragraph>
      </Section>

      {!isEmptyString(source) || !isCrossing ? (
        <Section title="Other information">
          {!isCrossing ? (
            <Entry>
              <Field>SARP ID:</Field> {sarpid}
            </Entry>
          ) : null}

          {!isEmptyString(source) ? (
            <Entry>
              <Field>Source:</Field> {source}
            </Entry>
          ) : null}
        </Section>
      ) : null}
    </Box>
  )
}

BarrierDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  hasnetwork: PropTypes.number.isRequired,
  excluded: PropTypes.number,
  source: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
  HUC8: PropTypes.string,
  HUC12: PropTypes.string,
  HUC8Name: PropTypes.string,
  HUC12Name: PropTypes.string,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  constriction: PropTypes.number,
  condition: PropTypes.number,
  barrierseverity: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
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
}

BarrierDetails.defaultProps = {
  HUC8: null,
  HUC12: null,
  HUC8Name: null,
  HUC12Name: null,
  excluded: false,
  source: null,
  stream: null,
  intermittent: -1,
  road: null,
  roadtype: null,
  crossingtype: null,
  constriction: null,
  barrierseverity: null,
  condition: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
  ownertype: null,
  barrierownertype: null,
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
}

export default BarrierDetails
