import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { Envelope, ExclamationTriangle } from '@emotion-icons/fa-solid'

import { extractHabitat } from 'components/Data/Habitat'
import { Entry, Field, Section } from 'components/Sidebar'

import {
  barrierTypeLabelSingular,
  siteMetadata,
  HAZARD,
  CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  FEASIBILITYCLASS,
  RECON,
  PASSABILITY,
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

const { version: dataVersion } = siteMetadata

const DamDetails = (barrier) => {
  const {
    barrierType,
    sarpid,
    condition,
    construction,
    diversion,
    estimated,
    feasibilityclass,
    flowstoocean,
    hasnetwork,
    hazard,
    height,
    invasive,
    lowheaddam,
    milestooutlet,
    passability,
    passagefacility,
    purpose,
    recon,
    removed,
    totalmainstemupstreammiles,
    totalmainstemdownstreammiles,
    yearcompleted,
    yearremoved,
    invasivenetwork,
  } = barrier

  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]
  const isLowheadDam = lowheaddam === 1 || lowheaddam === 2
  const isDiversion = diversion !== null && diversion >= 1
  const isUnspecifiedType = !(isLowheadDam || isDiversion || invasive)
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
            {isLowheadDam ? (
              <>
                {lowheaddam === 2 ? 'likely ' : null}
                lowhead dam{' '}
              </>
            ) : null}
            {isDiversion ? (
              <>
                {isLowheadDam ? <br /> : null}
                {diversion === 2 ? 'likely ' : null} water diversion
              </>
            ) : null}

            {isUnspecifiedType ? 'dam' : null}
            {invasive ? (
              <>
                <br />
                invasive species barrier
              </>
            ) : null}
          </Field>

          {estimated === 1 ? (
            <Flex sx={{ alignItems: 'flex-start', mt: '0.5rem' }}>
              <Box sx={{ color: 'grey.4', flex: '0 0 auto', mr: '0.5em' }}>
                <ExclamationTriangle size="2.25em" />
              </Box>
              <Text variant="help" sx={{ flex: '1 1 auto', fontSize: 0 }}>
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

        <LocationInfo {...barrier} />
      </Section>

      <Section title="Construction information">
        {purpose !== null && purpose >= 0 && PURPOSE[purpose] ? (
          <Entry>
            <Field label="Purpose" isUnknown={purpose === 0}>
              {PURPOSE[purpose].toLowerCase()}
            </Field>
          </Entry>
        ) : null}

        {yearcompleted > 0 ? (
          <Entry>
            <Field label="Constructed completed">{yearcompleted}</Field>
          </Entry>
        ) : null}
        {height > 0 ? (
          <Entry>
            <Field label="Height">{height} feet</Field>
          </Entry>
        ) : null}
        {construction !== null &&
        construction >= 0 &&
        CONSTRUCTION[construction] ? (
          <Entry>
            <Field label="Construction material" isUnknown={construction === 0}>
              {CONSTRUCTION[construction].toLowerCase()}
            </Field>
          </Entry>
        ) : null}

        {hazard !== null && hazard > 0 && HAZARD[hazard] ? (
          <Entry>
            <Field label="Hazard rating">{HAZARD[hazard].toLowerCase()}</Field>
          </Entry>
        ) : null}

        {condition !== null && condition >= 0 && CONDITION[condition] ? (
          <Entry>
            <Field label="Structural condition" isUnknown={condition === 0}>
              {CONDITION[condition].toLowerCase()}
            </Field>
          </Entry>
        ) : null}

        {!removed && passability !== null ? (
          <Entry>
            <Field label="Passability" isUnknown={passability === 0}>
              {PASSABILITY[passability]}
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
          <FunctionalNetworkInfo {...barrier} />
        ) : (
          <NoNetworkInfo {...barrier} />
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

      {(hasnetwork && totalmainstemupstreammiles > 0) ||
      totalmainstemdownstreammiles > 0 ? (
        <Section title="Mainstem network information">
          <MainstemNetworkInfo {...barrier} />
        </Section>
      ) : null}

      <Section title="Species information for this subwatershed">
        <SpeciesWatershedPresenceInfo {...barrier} />
      </Section>

      {!removed && feasibilityclass && feasibilityclass <= 10 ? (
        <Section title="Feasibility & conservation benefit">
          <Entry>
            <Field label="Feasibility" isUnknown={feasibilityclass <= 1}>
              {FEASIBILITYCLASS[feasibilityclass]}
              <br />
              <a
                href={`mailto:Kat@southeastaquatics.net?subject=Update feasibility for dam: ${sarpid} (data version: ${dataVersion})&body=The feasibility of this barrier should be: %0D%0A%0D%0A(choose one of the following options)%0D%0A%0D%0A${Object.entries(
                  FEASIBILITYCLASS
                )
                  // eslint-disable-next-line no-unused-vars
                  .filter(([key, _]) => key >= 1)
                  // eslint-disable-next-line no-unused-vars
                  .map(([_, value]) => value)
                  .join('%0D%0A')})`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Flex
                  sx={{ gap: '0.25rem', alignItems: 'center', fontSize: 0 }}
                >
                  <Envelope size="1rem" />
                  submit {feasibilityclass > 1 ? 'new' : null} feasibility
                </Flex>
              </a>
            </Field>

            {recon !== null && recon > 0 ? (
              <>
                <br />
                <Field label="Field recon notes">{RECON[recon]}</Field>
              </>
            ) : null}
          </Entry>
        </Section>
      ) : null}

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

DamDetails.propTypes = {
  ...BarrierPropType,
  barrierownertype: PropTypes.number,
  condition: PropTypes.number,
  construction: PropTypes.number,
  diversion: PropTypes.number,
  estimated: PropTypes.bool,
  feasibilityclass: PropTypes.number,
  hazard: PropTypes.number,
  height: PropTypes.number,
  lowheaddam: PropTypes.number,
  passability: PropTypes.number,
  passagefacility: PropTypes.number,
  purpose: PropTypes.number,
  recon: PropTypes.number,
  yearcompleted: PropTypes.number,
  yearremoved: PropTypes.number,
}

DamDetails.defaultProps = {
  ...BarrierDefaultProps,
  barrierownertype: null,
  condition: null,
  construction: null,
  diversion: 0,
  estimated: false,
  feasibilityclass: 0,
  hazard: null,
  height: 0,
  lowheaddam: null,
  passability: null,
  passagefacility: null,
  purpose: null,
  recon: null,
  yearcompleted: 0,
  yearremoved: 0,
}

export default DamDetails
