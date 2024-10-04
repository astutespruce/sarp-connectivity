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
  lat,
  lon,
  annualflow,
  barrierownertype,
  basin,
  congressionaldistrict,
  crossingtype,
  ejtract,
  ejtribal,
  fishhabitatpartnership,
  huc12,
  intermittent,
  nativeterritories,
  onloop,
  ownertype,
  regionalsgcnspp,
  road,
  roadtype,
  salmonidesu,
  snapped,
  source,
  sourceid,
  statesgcnspp,
  river,
  streamorder,
  streamsizeclass,
  subwatershed,
  tespp,
  trout,
  wildscenicriver,
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
        annualflow={annualflow}
        reachName={river}
        basin={basin}
        subwatershed={subwatershed}
        huc12={huc12}
        congressionaldistrict={congressionaldistrict}
        ownertype={ownertype}
        barrierownertype={barrierownertype}
        ejtract={ejtract}
        ejtribal={ejtribal}
        fishhabitatpartnership={fishhabitatpartnership}
        nativeterritories={nativeterritories}
        intermittent={intermittent}
        streamorder={streamorder}
        streamsizeclass={streamsizeclass}
        wildscenicriver={wildscenicriver}
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
      <IDInfo
        barrierType={barrierType}
        sarpid={sarpid}
        lat={lat}
        lon={lon}
        source={source}
        sourceid={sourceid}
      />
    </Section>
  </Box>
)

RoadCrossingDetails.propTypes = {
  annualflow: PropTypes.number,
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  barrierownertype: PropTypes.number,
  basin: PropTypes.string,
  congressionaldistrict: PropTypes.string,
  crossingtype: PropTypes.number,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  fishhabitatpartnership: PropTypes.string,
  huc12: PropTypes.string,
  intermittent: PropTypes.number,
  nativeterritories: PropTypes.string,
  onloop: PropTypes.bool,
  ownertype: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  road: PropTypes.string,
  roadtype: PropTypes.number,
  salmonidesu: PropTypes.string,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  sourceid: PropTypes.string,
  statesgcnspp: PropTypes.number,
  river: PropTypes.string,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  subwatershed: PropTypes.string,
  tespp: PropTypes.number,
  trout: PropTypes.number,
  wildscenicriver: PropTypes.string,
}

RoadCrossingDetails.defaultProps = {
  annualflow: null,
  basin: null,
  congressionaldistrict: null,
  crossingtype: null,
  ejtract: false,
  ejtribal: false,
  fishhabitatpartnership: null,
  huc12: null,
  intermittent: -1,
  nativeterritories: null,
  onloop: false,
  barrierownertype: null,
  ownertype: null,
  regionalsgcnspp: 0,
  road: null,
  roadtype: null,
  salmonidesu: null,
  snapped: true,
  source: null,
  sourceid: null,
  statesgcnspp: 0,
  river: null,
  streamorder: 0,
  streamsizeclass: null,
  subwatershed: null,
  tespp: 0,
  trout: 0,
  wildscenicriver: null,
}

export default RoadCrossingDetails
