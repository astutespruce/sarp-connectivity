import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

import { CROSSING_TYPE, ROAD_TYPE, barrierTypeLabelSingular } from 'config'

import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo'
import { BarrierPropType, BarrierDefaultProps } from './proptypes'

const RoadCrossingDetails = (barrier) => {
  const {
    barrierType,
    crossingtype,
    diadromoushabitat,
    intermittent,
    road,
    roadtype,
  } = barrier

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
          <Field label="Barrier type">Road / stream crossing</Field>
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
        {intermittent === 1 ? (
          <Entry>On a reach that has intermittent or ephemeral flow</Entry>
        ) : null}
      </Section>

      {diadromoushabitat === 1 ? (
        <Section title="Species habitat information for this network">
          <Entry>
            This {barrierTypeLabelSingular[barrierType]} is located on a reach
            with anadromous / catadromous species habitat.
          </Entry>
          <Text sx={{ fontSize: 0, color: 'grey.8' }}>
            Note: species habitat network statistics are not available for this{' '}
            {barrierTypeLabelSingular[barrierType]}.
          </Text>
        </Section>
      ) : null}

      <Section title="Functional network information">
        <NoNetworkInfo {...barrier} />
      </Section>

      <Section title="Species information for this subwatershed">
        <SpeciesWatershedPresenceInfo {...barrier} />
      </Section>

      <Section title="Other information">
        <IDInfo {...barrier} />
      </Section>
    </Box>
  )
}

RoadCrossingDetails.propTypes = {
  ...BarrierPropType,
  barrierownertype: PropTypes.number,
  crossingtype: PropTypes.number,
  ownertype: PropTypes.number,
  resurveyed: PropTypes.number,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  yearsurveyed: PropTypes.number,
}

RoadCrossingDetails.defaultProps = {
  ...BarrierDefaultProps,
  crossingtype: null,
  barrierownertype: null,
  ownertype: null,
  resurveyed: 0,
  road: null,
  roadtype: null,
  yearsurveyed: 0,
}

export default RoadCrossingDetails
