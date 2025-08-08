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
import { HabitatPropTypeStub, HabitatDefaultPropStub } from './proptypes'

const WaterfallDetails = ({
  barrierType,
  networkType,
  sarpid,
  lat,
  lon,
  alteredupstreammiles,
  alteredmainstemupstreammiles,
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
  perennialmainstemupstreammiles,
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
  totalmainstemupstreammiles,
  trout,
  unalteredupstreammiles,
  unalteredmainstemupstreammiles,
  unalteredwaterbodyacres,
  unalteredwetlandacres,
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
            unalteredwaterbodyacres={unalteredwaterbodyacres}
            unalteredwetlandacres={unalteredwetlandacres}
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

      {hasnetwork && totalmainstemupstreammiles > 0 ? (
        <Section title="Mainstem network information">
          <MainstemNetworkInfo
            barrierType={barrierType}
            networkType={networkType}
            flowstoocean={flowstoocean}
            flowstogreatlakes={flowstogreatlakes}
            totaldownstreamdams={totaldownstreamdams}
            totaldownstreamsmallbarriers={totaldownstreamsmallbarriers}
            totaldownstreamwaterfalls={totaldownstreamwaterfalls}
            totalmainstemupstreammiles={totalmainstemupstreammiles}
            perennialmainstemupstreammiles={perennialmainstemupstreammiles}
            alteredmainstemupstreammiles={alteredmainstemupstreammiles}
            unalteredmainstemupstreammiles={unalteredmainstemupstreammiles}
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
  alteredmainstemupstreammiles: PropTypes.number,
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
  perennialmainstemupstreammiles: PropTypes.number,
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
  totalmainstemupstreammiles: PropTypes.number,
  trout: PropTypes.string,
  unalteredupstreammiles: PropTypes.number,
  unalteredmainstemupstreammiles: PropTypes.number,
  unalteredwaterbodyacres: PropTypes.number,
  unalteredwetlandacres: PropTypes.number,
  wilderness: PropTypes.number,
  wildscenicriver: PropTypes.number,
  invasive: PropTypes.bool,
  invasivenetwork: PropTypes.number,
  ...HabitatPropTypeStub,
}

WaterfallDetails.defaultProps = {
  alteredupstreammiles: 0,
  alteredmainstemupstreammiles: 0,
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
  perennialmainstemupstreammiles: 0,
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
  totalmainstemupstreammiles: 0,
  trout: null,
  unalteredupstreammiles: 0,
  unalteredmainstemupstreammiles: 0,
  unalteredwaterbodyacres: 0,
  unalteredwetlandacres: 0,
  wilderness: null,
  wildscenicriver: null,
  invasive: false,
  invasivenetwork: 0,
  ...HabitatDefaultPropStub,
}

export default WaterfallDetails
