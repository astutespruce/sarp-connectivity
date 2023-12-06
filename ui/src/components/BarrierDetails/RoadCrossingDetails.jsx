import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

import { CROSSING_TYPE, ROAD_TYPE } from 'config'

import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo'

const RoadCrossingDetails = ({
  barrierType,
  networkType,
  sarpid,

  basin,
  crossingtype,
  ejtract,
  ejtribal,
  huc12,
  intermittent,
  onloop,
  ownertype,
  regionalsgcnspp,
  road,
  roadtype,
  salmonidesu,
  snapped,
  source,
  statesgcnspp,
  stream,
  streamorder,
  streamsizeclass,
  subwatershed,
  tespp,
  trout,
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
        barrierType={barrierType}
        reachName={stream}
        basin={basin}
        subwatershed={subwatershed}
        huc12={huc12}
        ownertype={ownertype}
        ejtract={ejtract}
        ejtribal={ejtribal}
        intermittent={intermittent}
        streamorder={streamorder}
        streamsizeclass={streamsizeclass}
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
      <NoNetworkInfo
        barrierType={barrierType}
        networkType={networkType}
        snapped={snapped}
        onloop={onloop}
      />
    </Section>

    {/* Note: diadromous species info not shown because these have no network */}

    <Section title="Species information for this subwatershed">
      <SpeciesWatershedPresenceInfo
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
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,

  basin: PropTypes.string,
  crossingtype: PropTypes.number,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  huc12: PropTypes.string,
  intermittent: PropTypes.number,
  onloop: PropTypes.bool,
  ownertype: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  salmonidesu: PropTypes.string,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  statesgcnspp: PropTypes.number,
  stream: PropTypes.string,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  subwatershed: PropTypes.string,
  tespp: PropTypes.number,
  trout: PropTypes.number,
}

RoadCrossingDetails.defaultProps = {
  basin: null,
  crossingtype: null,
  ejtract: false,
  ejtribal: false,
  huc12: null,
  intermittent: -1,
  onloop: false,
  ownertype: null,
  regionalsgcnspp: 0,
  road: null,
  roadtype: null,
  salmonidesu: null,
  snapped: true,
  source: null,
  statesgcnspp: 0,
  stream: null,
  streamorder: 0,
  streamsizeclass: null,
  subwatershed: null,
  tespp: 0,
  trout: 0,
}

export default RoadCrossingDetails
