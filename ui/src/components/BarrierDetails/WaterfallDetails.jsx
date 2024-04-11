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
import NetworkInfo from './NetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo'
import SpeciesHabitatInfo from './SpeciesHabitatInfo'

const WaterfallDetails = ({
  barrierType,
  networkType,
  sarpid,
  lat,
  lon,

  alteredupstreammiles,
  basin,
  excluded,
  falltype,
  flowstoocean,
  flowstogreatlakes,
  freealtereddownstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freeunaltereddownstreammiles,
  freeresilientdownstreammiles,
  hasnetwork,
  huc12,
  in_network_type,
  intermittent,
  landcover,
  milestooutlet,
  nativeterritories,
  onloop,
  passability,
  percentresilient,
  perennialupstreammiles,
  regionalsgcnspp,
  salmonidesu,
  sizeclasses,
  snapped,
  source,
  sourceid,
  statesgcnspp,
  resilientupstreammiles,
  river,
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
  invasive,
  invasivenetwork,
  ...props // includes species habitat fields selected dynamically
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]
  const habitat = hasnetwork ? extractHabitat(props) : []

  return (
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
          reachName={river}
          basin={basin}
          subwatershed={subwatershed}
          huc12={huc12}
          nativeterritories={nativeterritories}
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
            resilientupstreammiles={resilientupstreammiles}
            freedownstreammiles={freedownstreammiles}
            freeperennialdownstreammiles={freeperennialdownstreammiles}
            freealtereddownstreammiles={freealtereddownstreammiles}
            freeunaltereddownstreammiles={freeunaltereddownstreammiles}
            freeresilientdownstreammiles={freeresilientdownstreammiles}
            percentresilient={percentresilient}
            sizeclasses={sizeclasses}
            landcover={landcover}
            intermittent={intermittent}
            flowstoocean={flowstoocean}
            flowstogreatlakes={flowstogreatlakes}
            totaldownstreamdams={totaldownstreamdams}
            totaldownstreamsmallbarriers={totaldownstreamsmallbarriers}
            totaldownstreamwaterfalls={totaldownstreamwaterfalls}
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

      {hasnetwork && habitat.length > 0 ? (
        <Section title="Species habitat information for this network">
          <SpeciesHabitatInfo habitat={habitat} />
        </Section>
      ) : null}

      {hasnetwork && flowstoocean && milestooutlet < 500 ? (
        <Section title="Diadromous species information">
          <DiadromousInfo
            barrierType={barrierType}
            milestooutlet={milestooutlet}
            totaldownstreamdams={totaldownstreamdams}
            totaldownstreamsmallbarriers={totaldownstreamsmallbarriers}
            totaldownstreamwaterfalls={totaldownstreamwaterfalls}
            {...props}
          />
        </Section>
      ) : null}

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
}

WaterfallDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,

  hasnetwork: PropTypes.bool.isRequired,
  alteredupstreammiles: PropTypes.number,
  basin: PropTypes.string,
  excluded: PropTypes.bool,
  falltype: PropTypes.string,
  flowstoocean: PropTypes.number,
  flowstogreatlakes: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  freeresilientdownstreammiles: PropTypes.number,
  huc12: PropTypes.string,
  nativeterritories: PropTypes.string,
  in_network_type: PropTypes.bool,
  intermittent: PropTypes.number,
  landcover: PropTypes.number,
  milestooutlet: PropTypes.number,
  onloop: PropTypes.bool,
  passability: PropTypes.number,
  percentresilient: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  salmonidesu: PropTypes.string,
  sizeclasses: PropTypes.number,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  sourceid: PropTypes.string,
  statesgcnspp: PropTypes.number,
  resilientupstreammiles: PropTypes.number,
  river: PropTypes.string,
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
  invasive: PropTypes.bool,
  invasivenetwork: PropTypes.number,
  alewifehabitatupstreammiles: PropTypes.number,
  freealewifehabitatdownstreammiles: PropTypes.number,
  americaneelhabitatupstreammiles: PropTypes.number,
  freeamericaneelhabitatdownstreammiles: PropTypes.number,
  americanshadhabitatupstreammiles: PropTypes.number,
  freeamericanshadhabitatdownstreammiles: PropTypes.number,
  atlanticsturgeonhabitatupstreammiles: PropTypes.number,
  freeatlanticsturgeonhabitatdownstreammiles: PropTypes.number,
  bluebackherringhabitatupstreammiles: PropTypes.number,
  freebluebackherringhabitatdownstreammiles: PropTypes.number,
  bonnevillecutthroattrouthabitatupstreammiles: PropTypes.number,
  freebonnevillecutthroattrouthabitatdownstreammiles: PropTypes.number,
  bulltrouthabitatupstreammiles: PropTypes.number,
  freebulltrouthabitatdownstreammiles: PropTypes.number,
  cabaselinefishhabitatupstreammiles: PropTypes.number,
  freecabaselinefishhabitatdownstreammiles: PropTypes.number,
  chesapeakediadromoushabitatupstreammiles: PropTypes.number,
  freechesapeakediadromoushabitatdownstreammiles: PropTypes.number,
  chinooksalmonhabitatupstreammiles: PropTypes.number,
  freechinooksalmonhabitatdownstreammiles: PropTypes.number,
  chumsalmonhabitatupstreammiles: PropTypes.number,
  freechumsalmonhabitatdownstreammiles: PropTypes.number,
  coastalcutthroattrouthabitatupstreammiles: PropTypes.number,
  freecoastalcutthroattrouthabitatdownstreammiles: PropTypes.number,
  cohosalmonhabitatupstreammiles: PropTypes.number,
  freecohosalmonhabitatdownstreammiles: PropTypes.number,
  easternbrooktrouthabitatupstreammiles: PropTypes.number,
  freeeasternbrooktrouthabitatdownstreammiles: PropTypes.number,
  greensturgeonhabitatupstreammiles: PropTypes.number,
  freegreensturgeonhabitatdownstreammiles: PropTypes.number,
  hickoryshadhabitatupstreammiles: PropTypes.number,
  freehickoryshadhabitatdownstreammiles: PropTypes.number,
  kokaneehabitatupstreammiles: PropTypes.number,
  freekokaneehabitatdownstreammiles: PropTypes.number,
  pacificlampreyhabitatupstreammiles: PropTypes.number,
  freepacificlampreyhabitatdownstreammiles: PropTypes.number,
  pinksalmonhabitatupstreammiles: PropTypes.number,
  freepinksalmonhabitatdownstreammiles: PropTypes.number,
  rainbowtrouthabitatupstreammiles: PropTypes.number,
  freerainbowtrouthabitatdownstreammiles: PropTypes.number,
  redbandtrouthabitatupstreammiles: PropTypes.number,
  freeredbandtrouthabitatdownstreammiles: PropTypes.number,
  shortnosesturgeonhabitatupstreammiles: PropTypes.number,
  freeshortnosesturgeonhabitatdownstreammiles: PropTypes.number,
  sockeyesalmonhabitatupstreammiles: PropTypes.number,
  freesockeyesalmonhabitatdownstreammiles: PropTypes.number,
  southatlanticanadromoushabitatupstreammiles: PropTypes.number,
  freesouthatlanticanadromoushabitatdownstreammiles: PropTypes.number,
  steelheadhabitatupstreammiles: PropTypes.number,
  freesteelheadhabitatdownstreammiles: PropTypes.number,
  streamnetanadromoushabitatupstreammiles: PropTypes.number,
  freestreamnetanadromoushabitatdownstreammiles: PropTypes.number,
  stripedbasshabitatupstreammiles: PropTypes.number,
  freestripedbasshabitatdownstreammiles: PropTypes.number,
  westslopecutthroattrouthabitatupstreammiles: PropTypes.number,
  freewestslopecutthroattrouthabitatdownstreammiles: PropTypes.number,
  whitesturgeonhabitatupstreammiles: PropTypes.number,
  freewhitesturgeonhabitatdownstreammiles: PropTypes.number,
  yellowstonecutthroattrouthabitatupstreammiles: PropTypes.number,
  freeyellowstonecutthroattrouthabitatdownstreammiles: PropTypes.number,
}

WaterfallDetails.defaultProps = {
  alteredupstreammiles: 0,
  basin: null,
  excluded: false,
  falltype: null,
  flowstoocean: 0,
  flowstogreatlakes: 0,
  freealtereddownstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  freeresilientdownstreammiles: 0,
  huc12: null,
  nativeterritories: null,
  in_network_type: false,
  intermittent: -1,
  landcover: null,
  milestooutlet: 0,
  onloop: false,
  passability: null,
  percentresilient: 0,
  perennialupstreammiles: 0,
  regionalsgcnspp: 0,
  salmonidesu: null,
  sizeclasses: null,
  snapped: false,
  source: null,
  sourceid: null,
  statesgcnspp: 0,
  resilientupstreammiles: 0,
  river: null,
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
  invasive: false,
  invasivenetwork: 0,
  alewifehabitatupstreammiles: 0,
  freealewifehabitatdownstreammiles: 0,
  americaneelhabitatupstreammiles: 0,
  freeamericaneelhabitatdownstreammiles: 0,
  americanshadhabitatupstreammiles: 0,
  freeamericanshadhabitatdownstreammiles: 0,
  atlanticsturgeonhabitatupstreammiles: 0,
  freeatlanticsturgeonhabitatdownstreammiles: 0,
  bluebackherringhabitatupstreammiles: 0,
  freebluebackherringhabitatdownstreammiles: 0,
  bonnevillecutthroattrouthabitatupstreammiles: 0,
  freebonnevillecutthroattrouthabitatdownstreammiles: 0,
  bulltrouthabitatupstreammiles: 0,
  freebulltrouthabitatdownstreammiles: 0,
  cabaselinefishhabitatupstreammiles: 0,
  freecabaselinefishhabitatdownstreammiles: 0,
  chesapeakediadromoushabitatupstreammiles: 0,
  freechesapeakediadromoushabitatdownstreammiles: 0,
  chinooksalmonhabitatupstreammiles: 0,
  freechinooksalmonhabitatdownstreammiles: 0,
  chumsalmonhabitatupstreammiles: 0,
  freechumsalmonhabitatdownstreammiles: 0,
  coastalcutthroattrouthabitatupstreammiles: 0,
  freecoastalcutthroattrouthabitatdownstreammiles: 0,
  cohosalmonhabitatupstreammiles: 0,
  freecohosalmonhabitatdownstreammiles: 0,
  easternbrooktrouthabitatupstreammiles: 0,
  freeeasternbrooktrouthabitatdownstreammiles: 0,
  greensturgeonhabitatupstreammiles: 0,
  freegreensturgeonhabitatdownstreammiles: 0,
  hickoryshadhabitatupstreammiles: 0,
  freehickoryshadhabitatdownstreammiles: 0,
  kokaneehabitatupstreammiles: 0,
  freekokaneehabitatdownstreammiles: 0,
  pacificlampreyhabitatupstreammiles: 0,
  freepacificlampreyhabitatdownstreammiles: 0,
  pinksalmonhabitatupstreammiles: 0,
  freepinksalmonhabitatdownstreammiles: 0,
  rainbowtrouthabitatupstreammiles: 0,
  freerainbowtrouthabitatdownstreammiles: 0,
  redbandtrouthabitatupstreammiles: 0,
  freeredbandtrouthabitatdownstreammiles: 0,
  shortnosesturgeonhabitatupstreammiles: 0,
  freeshortnosesturgeonhabitatdownstreammiles: 0,
  sockeyesalmonhabitatupstreammiles: 0,
  freesockeyesalmonhabitatdownstreammiles: 0,
  southatlanticanadromoushabitatupstreammiles: 0,
  freesouthatlanticanadromoushabitatdownstreammiles: 0,
  steelheadhabitatupstreammiles: 0,
  freesteelheadhabitatdownstreammiles: 0,
  streamnetanadromoushabitatupstreammiles: 0,
  freestreamnetanadromoushabitatdownstreammiles: 0,
  stripedbasshabitatupstreammiles: 0,
  freestripedbasshabitatdownstreammiles: 0,
  westslopecutthroattrouthabitatupstreammiles: 0,
  freewestslopecutthroattrouthabitatdownstreammiles: 0,
  whitesturgeonhabitatupstreammiles: 0,
  freewhitesturgeonhabitatdownstreammiles: 0,
  yellowstonecutthroattrouthabitatupstreammiles: 0,
  freeyellowstonecutthroattrouthabitatdownstreammiles: 0,
}

export default WaterfallDetails
