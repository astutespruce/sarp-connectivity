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
  source,
  hasnetwork,
  excluded,
  in_network_type,
  onloop,
  snapped,
  stream,
  intermittent,
  huc12,
  basin,
  subwatershed,
  falltype,
  passability,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  streamorder,
  streamsizeclass,
  waterbodysizeclass,
  waterbodykm2,
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
  flowstoocean,
  milestooutlet,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
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
        // <>
        //   {excluded ? (
        //     <Entry>
        //       This waterfall was excluded from the connectivity analysis based
        //       on field reconnaissance or manual review of aerial imagery.
        //     </Entry>
        //   ) : (
        //     <Entry>
        //       <Text>
        //         This waterfall is off-network and has no functional network
        //         information.
        //       </Text>
        //       <Paragraph variant="help" sx={{ mt: '1rem' }}>
        //         Not all barriers could be correctly snapped to the aquatic
        //         network for analysis. Please contact us to report an error or
        //         for assistance interpreting these results.
        //       </Paragraph>
        //     </Entry>
        //   )}
        // </>
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
        <IDInfo source={source} />
      </Section>
    ) : null}
  </Box>
)

WaterfallDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  in_network_type: PropTypes.bool,
  onloop: PropTypes.bool,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
  huc12: PropTypes.string,
  basin: PropTypes.string,
  subwatershed: PropTypes.string,
  falltype: PropTypes.string,
  passability: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
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
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  flowstoocean: PropTypes.number,
  milestooutlet: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
}

WaterfallDetails.defaultProps = {
  huc12: null,
  basin: null,
  subwatershed: null,
  excluded: false,
  in_network_type: false,
  onloop: false,
  snapped: false,
  source: null,
  stream: null,
  intermittent: -1,
  falltype: null,
  passability: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
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
  streamorder: 0,
  streamsizeclass: null,
  waterbodykm2: -1,
  waterbodysizeclass: null,
  flowstoocean: 0,
  milestooutlet: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
}

export default WaterfallDetails
