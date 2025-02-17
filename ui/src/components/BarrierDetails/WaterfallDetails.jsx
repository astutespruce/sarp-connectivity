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

const WaterfallDetails = ({
  barrierType,
  networkType,
  sarpid,
  lat,
  lon,
  alteredupstreammiles,
  alteredupstreammainstemmiles,
  annualflow,
  basin,
  coldupstreammiles,
  congressionaldistrict,
  diadromoushabitat,
  excluded,
  falltype,
  fishhabitatpartnership,
  flowstoocean,
  flowstogreatlakes,
  freealtereddownstreammiles,
  freealteredlineardownstreammiles,
  freecolddownstreammiles,
  freedownstreammiles,
  freelineardownstreammiles,
  freeperennialdownstreammiles,
  freeperenniallineardownstreammiles,
  freeunaltereddownstreammiles,
  freeunalteredlineardownstreammiles,
  freeresilientdownstreammiles,
  hasnetwork,
  huc12,
  in_network_type,
  intermittent,
  canal,
  landcover,
  mainstemsizeclasses,
  milestooutlet,
  nativeterritories,
  onloop,
  partnerid,
  passability,
  percentcold,
  percentresilient,
  perennialupstreammiles,
  perennialupstreammainstemmiles,
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
  totalupstreammainstemmiles,
  trout,
  unalteredupstreammiles,
  unalteredupstreammainstemmiles,
  upstreamunalteredwaterbodyacres,
  upstreamunalteredwetlandacres,
  wilderness,
  wildscenicriver,
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
          annualflow={annualflow}
          reachName={river}
          basin={basin}
          subwatershed={subwatershed}
          huc12={huc12}
          congressionaldistrict={congressionaldistrict}
          fishhabitatpartnership={fishhabitatpartnership}
          nativeterritories={nativeterritories}
          intermittent={intermittent}
          canal={canal}
          streamorder={streamorder}
          streamsizeclass={streamsizeclass}
          wilderness={wilderness}
          wildscenicriver={wildscenicriver}
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
          <FunctionalNetworkInfo
            barrierType={barrierType}
            networkType={networkType}
            totalupstreammiles={totalupstreammiles}
            perennialupstreammiles={perennialupstreammiles}
            alteredupstreammiles={alteredupstreammiles}
            unalteredupstreammiles={unalteredupstreammiles}
            resilientupstreammiles={resilientupstreammiles}
            coldupstreammiles={coldupstreammiles}
            freedownstreammiles={freedownstreammiles}
            freeperennialdownstreammiles={freeperennialdownstreammiles}
            freealtereddownstreammiles={freealtereddownstreammiles}
            freeunaltereddownstreammiles={freeunaltereddownstreammiles}
            freeresilientdownstreammiles={freeresilientdownstreammiles}
            freecolddownstreammiles={freecolddownstreammiles}
            percentresilient={percentresilient}
            percentcold={percentcold}
            sizeclasses={sizeclasses}
            landcover={landcover}
            intermittent={intermittent}
            flowstoocean={flowstoocean}
            flowstogreatlakes={flowstogreatlakes}
            totaldownstreamdams={totaldownstreamdams}
            totaldownstreamsmallbarriers={totaldownstreamsmallbarriers}
            totaldownstreamwaterfalls={totaldownstreamwaterfalls}
            upstreamunalteredwaterbodyacres={upstreamunalteredwaterbodyacres}
            upstreamunalteredwetlandacres={upstreamunalteredwetlandacres}
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
          <SpeciesHabitatInfo
            barrierType={barrierType}
            diadromoushabitat={diadromoushabitat}
            habitat={habitat}
          />
        </Section>
      ) : null}

      {hasnetwork && flowstoocean && milestooutlet < 500 ? (
        <Section title="Marine connectivity">
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

      {hasnetwork && totalupstreammainstemmiles > 0 ? (
        <Section title="Mainstem network information">
          <MainstemNetworkInfo
            barrierType={barrierType}
            networkType={networkType}
            flowstoocean={flowstoocean}
            flowstogreatlakes={flowstogreatlakes}
            totaldownstreamdams={totaldownstreamdams}
            totaldownstreamsmallbarriers={totaldownstreamsmallbarriers}
            totaldownstreamwaterfalls={totaldownstreamwaterfalls}
            totalupstreammainstemmiles={totalupstreammainstemmiles}
            perennialupstreammainstemmiles={perennialupstreammainstemmiles}
            alteredupstreammainstemmiles={alteredupstreammainstemmiles}
            unalteredupstreammainstemmiles={unalteredupstreammainstemmiles}
            freelineardownstreammiles={freelineardownstreammiles}
            freeperenniallineardownstreammiles={
              freeperenniallineardownstreammiles
            }
            freealteredlineardownstreammiles={freealteredlineardownstreammiles}
            freeunalteredlineardownstreammiles={
              freeunalteredlineardownstreammiles
            }
            mainstemsizeclasses={mainstemsizeclasses}
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
          partnerid={partnerid}
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
  alteredupstreammainstemmiles: PropTypes.number,
  annualflow: PropTypes.number,
  basin: PropTypes.string,
  coldupstreammiles: PropTypes.number,
  congressionaldistrict: PropTypes.string,
  diadromoushabitat: PropTypes.number,
  excluded: PropTypes.bool,
  falltype: PropTypes.string,
  fishhabitatpartnership: PropTypes.string,
  flowstoocean: PropTypes.number,
  flowstogreatlakes: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freealteredlineardownstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freelineardownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freeperenniallineardownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  freeunalteredlineardownstreammiles: PropTypes.number,
  freeresilientdownstreammiles: PropTypes.number,
  freecolddownstreammiles: PropTypes.number,
  huc12: PropTypes.string,
  nativeterritories: PropTypes.string,
  in_network_type: PropTypes.bool,
  intermittent: PropTypes.number,
  canal: PropTypes.number,
  landcover: PropTypes.number,
  mainstemsizeclasses: PropTypes.number,
  milestooutlet: PropTypes.number,
  onloop: PropTypes.bool,
  partnerid: PropTypes.string,
  passability: PropTypes.number,
  percentcold: PropTypes.number,
  percentresilient: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  perennialupstreammainstemmiles: PropTypes.number,
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
  totalupstreammainstemmiles: PropTypes.number,
  trout: PropTypes.string,
  unalteredupstreammiles: PropTypes.number,
  unalteredupstreammainstemmiles: PropTypes.number,
  upstreamunalteredwaterbodyacres: PropTypes.number,
  upstreamunalteredwetlandacres: PropTypes.number,
  wilderness: PropTypes.number,
  wildscenicriver: PropTypes.number,
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
  alteredupstreammainstemmiles: 0,
  annualflow: null,
  basin: null,
  coldupstreammiles: 0,
  congressionaldistrict: null,
  diadromoushabitat: 0,
  excluded: false,
  falltype: null,
  fishhabitatpartnership: null,
  flowstoocean: 0,
  flowstogreatlakes: 0,
  freealtereddownstreammiles: 0,
  freealteredlineardownstreammiles: 0,
  freecolddownstreammiles: 0,
  freedownstreammiles: 0,
  freelineardownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freeperenniallineardownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  freeunalteredlineardownstreammiles: 0,
  freeresilientdownstreammiles: 0,
  huc12: null,
  nativeterritories: null,
  in_network_type: false,
  intermittent: 0,
  canal: 0,
  landcover: null,
  mainstemsizeclasses: 0,
  milestooutlet: 0,
  onloop: false,
  partnerid: null,
  passability: null,
  percentcold: 0,
  percentresilient: 0,
  perennialupstreammiles: 0,
  perennialupstreammainstemmiles: 0,
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
  totalupstreammainstemmiles: 0,
  trout: null,
  unalteredupstreammiles: 0,
  unalteredupstreammainstemmiles: 0,
  upstreamunalteredwaterbodyacres: 0,
  upstreamunalteredwetlandacres: 0,
  wilderness: null,
  wildscenicriver: null,
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
