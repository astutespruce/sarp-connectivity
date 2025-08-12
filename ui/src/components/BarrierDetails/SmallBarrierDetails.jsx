import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { extractHabitat } from 'components/Data/Habitat'
import { Entry, Field, Section } from 'components/Sidebar'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import {
  barrierTypeLabelSingular,
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
import FunctionalNetworkInfo from './FunctionalNetworkInfo'
import MainstemNetworkInfo from './MainstemNetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo'
import SpeciesHabitatInfo from './SpeciesHabitatInfo'
import { BarrierPropType, BarrierDefaultProps } from './proptypes'

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

const BarrierDetails = (barrier) => {
  const {
    barrierType,
    networkType,
    barrierseverity,
    condition,
    constriction,
    crossingtype,
    excluded,
    flowstoocean,
    hasnetwork,
    in_network_type,
    invasive,
    invasivenetwork,
    milestooutlet,
    onloop,
    passagefacility,
    protocolused,
    removed,
    road,
    roadtype,
    sarp_score,
    snapped,
    totalmainstemupstreammiles,
    yearremoved,
  } = barrier

  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]
  const habitat = hasnetwork ? extractHabitat(barrier) : []

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
            Road-related <br />
            potential barrier
            {invasive ? (
              <>
                ,<br />
                invasive species barrier
              </>
            ) : null}
          </Field>
        </Entry>
        {!isEmptyString(road) ? (
          <Entry>
            <Field label="Road">{road}</Field>
          </Entry>
        ) : null}

        <LocationInfo {...barrier} />
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
        {!removed && barrierseverity !== null ? (
          <Entry>
            <Field label="Severity" isUnknown={barrierseverity === 0}>
              {SMALL_BARRIER_SEVERITY[barrierseverity]}
            </Field>
          </Entry>
        ) : null}
        {!removed && sarp_score >= 0 ? (
          <Entry>
            <Field label="SARP Aquatic Organism Passage score">
              {formatNumber(sarp_score, 1)}
              <Text sx={{ fontSize: 0, color: 'grey.8' }}>
                ({classifySARPScore(sarp_score)})
              </Text>
            </Field>
            {!isEmptyString(protocolused) ? (
              <Box sx={{ mt: '1rem' }}>
                <Field label="Protocol used">{protocolused}</Field>
              </Box>
            ) : null}
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
          <FunctionalNetworkInfo {...barrier} />
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

      {hasnetwork && habitat.length > 0 ? (
        <Section title="Species habitat information for this network">
          <SpeciesHabitatInfo {...barrier} habitat={habitat} />
        </Section>
      ) : null}

      {hasnetwork && flowstoocean && milestooutlet < 500 ? (
        <Section title="Marine connectivity">
          <DiadromousInfo {...barrier} />
        </Section>
      ) : null}

      {hasnetwork && totalmainstemupstreammiles > 0 ? (
        <Section title="Mainstem network information">
          <MainstemNetworkInfo {...barrier} />
        </Section>
      ) : null}

      <Section title="Species information for this subwatershed">
        <SpeciesWatershedPresenceInfo {...barrier} />
      </Section>

      {hasnetwork && (invasive || invasivenetwork === 1) ? (
        <Section title="Invasive species management">
          {!invasive && invasivenetwork === 1 ? (
            <Entry>
              Upstream of a barrier identified as a beneficial to restricting
              the movement of invasive species.
            </Entry>
          ) : null}

          {invasive ? (
            <Entry>
              This {barrierTypeLabel} is identified as a beneficial to
              restricting the movement of invasive species and is not ranked.
            </Entry>
          ) : null}
        </Section>
      ) : null}

      <Section title="Other information">
        <IDInfo {...barrier} />
      </Section>
    </Box>
  )
}

BarrierDetails.propTypes = {
  ...BarrierPropType,
  barrierownertype: PropTypes.number,
  barrierseverity: PropTypes.number,
  condition: PropTypes.number,
  constriction: PropTypes.number,
  crossingtype: PropTypes.number,
  excluded: PropTypes.bool,
  ownertype: PropTypes.number,
  protocolused: PropTypes.string,
  removed: PropTypes.bool,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  sarp_score: PropTypes.number,
  yearremoved: PropTypes.number,
}

BarrierDetails.defaultProps = {
  ...BarrierDefaultProps,
  barrierownertype: null,
  barrierseverity: null,
  condition: null,
  constriction: null,
  crossingtype: null,
  excluded: false,
  ownertype: null,
  passagefacility: null,
  protocolused: null,
  removed: false,
  road: null,
  roadtype: null,
  sarp_score: -1,
  yearremoved: 0,
}

export default BarrierDetails
