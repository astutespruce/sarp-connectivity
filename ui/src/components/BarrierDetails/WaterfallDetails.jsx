import React from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

import { PASSABILITY } from 'config'
import { Entry, Field, Section } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

import DiadromousInfo from './DiadromousInfo'
import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NetworkInfo from './NetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesInfo from './SpeciesInfo'

const WaterfallDetails = ({
  barrierType,
  networkType,
  sarpid,

  alteredupstreammiles,
  basin,
  excluded,
  falltype,
  flowstoocean,
  freealtereddownstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freeunaltereddownstreammiles,
  hasnetwork,
  huc12,
  in_network_type,
  intermittent,
  landcover,
  milestooutlet,
  onloop,
  passability,
  perennialupstreammiles,
  regionalsgcnspp,
  salmonidesu,
  sizeclasses,
  snapped,
  source,
  statesgcnspp,
  stream,
  streamorder,
  streamsizeclass,
  subwatershed,
  tespp,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  totalupstreammiles,
  trout,
  unalteredupstreammiles,
  waterbodykm2,
  waterbodysizeclass,
}) => (
  <Box
    sx={{
      mt: '-1rem',
      mx: '-0.5rem',
      fontSize: 1,
    }}
  >
    <Section title="Location">
      <LocationInfo
        barrierType={barrierType}
        reachName={stream}
        basin={basin}
        subwatershed={subwatershed}
        huc12={huc12}
        intermittent={intermittent}
        streamorder={streamorder}
        streamsizeclass={streamsizeclass}
        waterbodysizeclass={waterbodysizeclass}
        waterbodykm2={waterbodykm2}
      />

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
        <NetworkInfo
          barrierType={barrierType}
          networkType={networkType}
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

    {hasnetwork && flowstoocean && milestooutlet < 500 ? (
      <Section title="Diadromous species information">
        <DiadromousInfo
          barrierType={barrierType}
          milestooutlet={milestooutlet}
          totaldownstreamdams={totaldownstreamdams}
          totaldownstreamsmallbarriers={totaldownstreamsmallbarriers}
          totaldownstreamwaterfalls={totaldownstreamwaterfalls}
        />
      </Section>
    ) : null}

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

    {!isEmptyString(source) ? (
      <Section title="Other information">
        <IDInfo sarpid={sarpid} source={source} />
      </Section>
    ) : null}
  </Box>
)

WaterfallDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,

  hasnetwork: PropTypes.bool.isRequired,
  alteredupstreammiles: PropTypes.number,
  basin: PropTypes.string,
  excluded: PropTypes.bool,
  falltype: PropTypes.string,
  flowstoocean: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  huc12: PropTypes.string,
  in_network_type: PropTypes.bool,
  intermittent: PropTypes.number,
  landcover: PropTypes.number,
  milestooutlet: PropTypes.number,
  onloop: PropTypes.bool,
  passability: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  salmonidesu: PropTypes.string,
  sizeclasses: PropTypes.number,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  statesgcnspp: PropTypes.number,
  stream: PropTypes.string,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  subwatershed: PropTypes.string,
  tespp: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
  totalupstreammiles: PropTypes.number,
  trout: PropTypes.number,
  unalteredupstreammiles: PropTypes.number,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
}

WaterfallDetails.defaultProps = {
  alteredupstreammiles: 0,
  basin: null,
  excluded: false,
  falltype: null,
  flowstoocean: 0,
  freealtereddownstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  huc12: null,
  in_network_type: false,
  intermittent: -1,
  landcover: null,
  milestooutlet: 0,
  onloop: false,
  passability: null,
  perennialupstreammiles: 0,
  regionalsgcnspp: 0,
  salmonidesu: null,
  sizeclasses: null,
  snapped: false,
  source: null,
  statesgcnspp: 0,
  stream: null,
  streamorder: 0,
  streamsizeclass: null,
  subwatershed: null,
  tespp: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
  totalupstreammiles: 0,
  trout: 0,
  unalteredupstreammiles: 0,
  waterbodykm2: -1,
  waterbodysizeclass: null,
}

export default WaterfallDetails
