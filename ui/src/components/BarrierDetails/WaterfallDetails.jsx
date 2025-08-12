import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { barrierTypeLabelSingular, PASSABILITY } from 'config'
import { extractHabitat } from 'components/Data/Habitat'
import { Entry, Field, Section } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

import DiadromousInfo from './DiadromousInfo'
import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import FunctionalNetworkInfo from './FunctionalNetworkInfo'
import MainstemNetworkInfo from './MainstemNetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo'
import SpeciesHabitatInfo from './SpeciesHabitatInfo'
import { BarrierPropType, BarrierDefaultProps } from './proptypes'

const WaterfallDetails = (barrier) => {
  const {
    barrierType,
    falltype,
    flowstoocean,
    hasnetwork,
    milestooutlet,
    passability,
    totalmainstemupstreammiles,
    invasive,
    invasivenetwork,
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
        <LocationInfo {...barrier} />

        {falltype && !isEmptyString(falltype) ? (
          <Entry>
            <Field label="Waterfall type">{falltype}</Field>
          </Entry>
        ) : null}

        {passability !== null ? (
          <Entry>
            <Field label="Passability" isUnknown={passability === 0}>
              {PASSABILITY[passability]}
            </Field>
          </Entry>
        ) : null}
      </Section>

      <Section title="Functional network information">
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

WaterfallDetails.propTypes = {
  ...BarrierPropType,
  excluded: PropTypes.bool,
  falltype: PropTypes.string,
  partnerid: PropTypes.string,
  passability: PropTypes.number,
  invasive: PropTypes.bool,
}

WaterfallDetails.defaultProps = {
  ...BarrierDefaultProps,
  falltype: null,
  partnerid: null,
  passability: null,
  invasive: false,
}

export default WaterfallDetails
