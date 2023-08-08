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
  networkType,
  onloop,
  snapped,
  sarpid,
  source,
  stream,
  intermittent,
  huc12,
  basin,
  subwatershed,
  road,
  roadtype,
  crossingtype,
  disadvantagedcommunity,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  ownertype,
  streamorder,
  streamsizeclass,
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
        disadvantagedcommunity={disadvantagedcommunity}
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
  onloop: PropTypes.bool,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
  huc12: PropTypes.string,
  basin: PropTypes.string,
  subwatershed: PropTypes.string,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  crossingtype: PropTypes.number,
  disadvantagedcommunity: PropTypes.string,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
  ownertype: PropTypes.number,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
}

RoadCrossingDetails.defaultProps = {
  onloop: false,
  snapped: true,
  huc12: null,
  basin: null,
  subwatershed: null,
  source: null,
  stream: null,
  intermittent: -1,
  road: null,
  roadtype: null,
  crossingtype: null,
  disadvantagedcommunity: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
  ownertype: null,
  streamorder: 0,
  streamsizeclass: null,
}

export default RoadCrossingDetails
