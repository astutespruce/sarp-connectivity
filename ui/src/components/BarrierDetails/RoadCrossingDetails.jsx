import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

import { CROSSING_TYPE, ROAD_TYPE } from 'config'

import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesInfo from './SpeciesInfo'

const RoadCrossingDetails = ({
  barrierType,
  sarpid,
  source,
  stream,
  intermittent,
  HUC12,
  HUC8Name,
  HUC12Name,
  road,
  roadtype,
  crossingtype,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  ownertype,
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
        <Field label="Barrier type">Road / stream crossing</Field>
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
      {intermittent === 1 ? (
        <Entry>On a reach that has intermittent or ephemeral flow</Entry>
      ) : null}
    </Section>

    <Section title="Functional network information">
      <NoNetworkInfo barrierType={barrierType} />
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

    <Section title="Other information">
      <IDInfo sarpid={sarpid} source={source} />
    </Section>
  </Box>
)

RoadCrossingDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  source: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
  HUC12: PropTypes.string,
  HUC8Name: PropTypes.string,
  HUC12Name: PropTypes.string,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
  ownertype: PropTypes.number,
}

RoadCrossingDetails.defaultProps = {
  HUC12: null,
  HUC8Name: null,
  HUC12Name: null,
  source: null,
  stream: null,
  intermittent: -1,
  road: null,
  roadtype: null,
  crossingtype: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
  ownertype: null,
}

export default RoadCrossingDetails
