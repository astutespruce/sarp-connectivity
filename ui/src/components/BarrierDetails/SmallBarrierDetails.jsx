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
} from 'config'

import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NetworkInfo from './NetworkInfo'
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
  sarpid,
  source,
  hasnetwork,
  excluded,
  stream,
  intermittent,
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
        mx: '-0.5rem',
        fontSize: 1,
      }}
    >
      <Section title="Location">
        <Entry>
          <Field label="Barrier type">
            {isCrossing
              ? 'Road / stream crossing'
              : 'Road-related potential barrier'}
          </Field>
        </Entry>
        {!isEmptyString(road) ? (
          <Entry>
            <Field label="Road">{road}</Field>
          </Entry>
        ) : null}

        <LocationInfo
          reachName={stream}
          HUC8Name={HUC8Name}
          HUC12Name={HUC12Name}
          HUC12={HUC12}
          ownertype={ownertype}
          barrierownertype={barrierownertype}
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
              {BARRIER_SEVERITY[barrierseverity]}
            </Field>
          </Entry>
        ) : null}
        {!isCrossing && sarp_score >= 0 ? (
          <Entry>
            <Field label="SARP Aquatic Organism Passage score">
              {formatNumber(sarp_score, 1)} ({classifySARPScore(sarp_score)})
            </Field>
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
            intermittent={intermittent}
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
        <SpeciesInfo
          barrierType={barrierType}
          tespp={tespp}
          regionalsgcnspp={regionalsgcnspp}
          statesgcnspp={statesgcnspp}
          trout={trout}
          salmonidesu={salmonidesu}
        />
      </Section>

      {!isEmptyString(source) || !isCrossing ? (
        <Section title="Other information">
          <IDInfo sarpid={!isCrossing ? sarpid : null} source={source} />
        </Section>
      ) : null}
    </Box>
  )
}

BarrierDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  hasnetwork: PropTypes.number.isRequired,
  excluded: PropTypes.number,
  source: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
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
