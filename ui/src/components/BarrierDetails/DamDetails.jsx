import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { Envelope, ExclamationTriangle } from '@emotion-icons/fa-solid'

import { extractHabitat } from 'components/Data/Habitat'
import { Entry, Field, Section } from 'components/Sidebar'

import {
  barrierTypeLabelSingular,
  siteMetadata,
  HAZARD,
  CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  FEASIBILITYCLASS,
  RECON,
  PASSABILITY,
} from 'config'

import DiadromousInfo from './DiadromousInfo'
import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NetworkInfo from './NetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo'
import SpeciesHabitatInfo from './SpeciesHabitatInfo'

const { version: dataVersion } = siteMetadata

const DamDetails = ({
  barrierType,
  networkType,
  sarpid,
  lat,
  lon,
  alteredupstreammiles,
  annualflow,
  barrierownertype,
  basin,
  condition,
  construction,
  costlower,
  costmean,
  costupper,
  diversion,
  ejtract,
  ejtribal,
  estimated,
  excluded,
  feasibilityclass,
  fedregulatoryagency,
  fercregulated,
  fishhabitatpartnership,
  flowstoocean,
  flowstogreatlakes,
  freealtereddownstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freeunaltereddownstreammiles,
  freeresilientdownstreammiles,
  hasnetwork,
  hazard,
  height,
  huc12,
  in_network_type,
  intermittent,
  invasive,
  landcover,
  link,
  lowheaddam,
  milestooutlet,
  nativeterritories,
  nidfederalid,
  nidid,
  onloop,
  ownertype,
  partnerid,
  passability,
  passagefacility,
  percentresilient,
  perennialupstreammiles,
  purpose,
  recon,
  regionalsgcnspp,
  removed,
  resilientupstreammiles,
  river,
  salmonidesu,
  sizeclasses,
  snapped,
  source,
  sourceid,
  stateregulated,
  statesgcnspp,
  storagevolume,
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
  unranked,
  waterbodykm2,
  waterbodysizeclass,
  waterright,
  yearcompleted,
  yearremoved,
  invasivenetwork,
  ...props // includes species habitat fields selected dynamically
}) => {
  const barrierTypeLabel = barrierTypeLabelSingular[barrierType]
  const isLowheadDam = lowheaddam === 1 || lowheaddam === 2
  const isDiversion = diversion !== null && diversion >= 1
  const isUnspecifiedType = !(isLowheadDam || isDiversion || invasive)
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
        <Entry>
          <Field label="Barrier type">
            {isLowheadDam ? (
              <>
                {lowheaddam === 2 ? 'likely ' : null}
                lowhead dam{' '}
              </>
            ) : null}
            {isDiversion ? (
              <>
                {isLowheadDam ? <br /> : null}
                {diversion === 2 ? 'likely ' : null} water diversion
              </>
            ) : null}

            {isUnspecifiedType ? 'dam' : null}
            {invasive ? (
              <>
                <br />
                invasive species barrier
              </>
            ) : null}
          </Field>

          {estimated === 1 ? (
            <Flex sx={{ alignItems: 'flex-start', mt: '0.5rem' }}>
              <Box sx={{ color: 'grey.4', flex: '0 0 auto', mr: '0.5em' }}>
                <ExclamationTriangle size="2.25em" />
              </Box>
              <Text variant="help" sx={{ flex: '1 1 auto', fontSize: 0 }}>
                Dam is estimated from other data sources and may be incorrect;
                please{' '}
                <a
                  href={`mailto:Kat@southeastaquatics.net?subject=Problem with Estimated Dam ${sarpid} (data version: ${dataVersion})`}
                >
                  let us know
                </a>
              </Text>
            </Flex>
          ) : null}
        </Entry>

        <LocationInfo
          barrierType={barrierType}
          annualflow={annualflow}
          reachName={river}
          basin={basin}
          subwatershed={subwatershed}
          huc12={huc12}
          ownertype={ownertype}
          barrierownertype={barrierownertype}
          fercregulated={fercregulated}
          stateregulated={stateregulated}
          fedregulatoryagency={fedregulatoryagency}
          waterright={waterright}
          costlower={costlower}
          costmean={costmean}
          costupper={costupper}
          ejtract={ejtract}
          ejtribal={ejtribal}
          fishhabitatpartnership={fishhabitatpartnership}
          nativeterritories={nativeterritories}
          intermittent={intermittent}
          storagevolume={storagevolume}
          streamorder={streamorder}
          streamsizeclass={streamsizeclass}
          waterbodysizeclass={waterbodysizeclass}
          waterbodykm2={waterbodykm2}
        />
      </Section>

      <Section title="Construction information">
        {purpose !== null && purpose >= 0 && PURPOSE[purpose] ? (
          <Entry>
            <Field label="Purpose" isUnknown={purpose === 0}>
              {PURPOSE[purpose].toLowerCase()}
            </Field>
          </Entry>
        ) : null}

        {yearcompleted > 0 ? (
          <Entry>
            <Field label="Constructed completed">{yearcompleted}</Field>
          </Entry>
        ) : null}
        {height > 0 ? (
          <Entry>
            <Field label="Height">{height} feet</Field>
          </Entry>
        ) : null}
        {construction !== null &&
        construction >= 0 &&
        CONSTRUCTION[construction] ? (
          <Entry>
            <Field label="Construction material" isUnknown={construction === 0}>
              {CONSTRUCTION[construction].toLowerCase()}
            </Field>
          </Entry>
        ) : null}

        {hazard !== null && hazard > 0 && HAZARD[hazard] ? (
          <Entry>
            <Field label="Hazard rating">{HAZARD[hazard].toLowerCase()}</Field>
          </Entry>
        ) : null}

        {condition !== null && condition >= 0 && CONDITION[condition] ? (
          <Entry>
            <Field label="Structural condition" isUnknown={condition === 0}>
              {CONDITION[condition].toLowerCase()}
            </Field>
          </Entry>
        ) : null}

        {!removed && passability !== null ? (
          <Entry>
            <Field label="Passability" isUnknown={passability === 0}>
              {PASSABILITY[passability]}
            </Field>
          </Entry>
        ) : null}

        {passagefacility !== null &&
        passagefacility >= 0 &&
        PASSAGEFACILITY[passagefacility] ? (
          <Entry>
            <Field
              label="Passage facility type"
              isUnknown={passagefacility === 0}
            >
              {PASSAGEFACILITY[passagefacility].toLowerCase()}
            </Field>
          </Entry>
        ) : null}
      </Section>

      <Section title="Functional network information">
        {removed ? (
          <Entry sx={{ mb: '1rem' }}>
            {yearremoved !== null && yearremoved > 0
              ? `This barrier was removed or mitigated in ${yearremoved}.`
              : 'This barrier has been removed or mitigated.'}
          </Entry>
        ) : null}

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
            waterbodysizeclass={waterbodysizeclass}
            waterbodykm2={waterbodykm2}
            intermittent={intermittent}
            invasive={invasive}
            unranked={unranked}
            removed={removed}
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
            diversion={diversion}
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

      {!removed && feasibilityclass && feasibilityclass <= 10 ? (
        <Section title="Feasibility & conservation benefit">
          <Entry>
            <Field label="Feasibility" isUnknown={feasibilityclass <= 1}>
              {FEASIBILITYCLASS[feasibilityclass]}
              <br />
              <a
                href={`mailto:Kat@southeastaquatics.net?subject=Update feasibility for dam: ${sarpid} (data version: ${dataVersion})&body=The feasibility of this barrier should be: %0D%0A%0D%0A(choose one of the following options)%0D%0A%0D%0A${Object.entries(
                  FEASIBILITYCLASS
                )
                  // eslint-disable-next-line no-unused-vars
                  .filter(([key, _]) => key >= 1)
                  // eslint-disable-next-line no-unused-vars
                  .map(([_, value]) => value)
                  .join('%0D%0A')})`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Flex
                  sx={{ gap: '0.25rem', alignItems: 'center', fontSize: 0 }}
                >
                  <Envelope size="1rem" />
                  submit {feasibilityclass > 1 ? 'new' : null} feasibility
                </Flex>
              </a>
            </Field>

            {recon !== null && recon > 0 ? (
              <>
                <br />
                <Field label="Field recon notes">{RECON[recon]}</Field>
              </>
            ) : null}
          </Entry>
        </Section>
      ) : null}

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
          nidfederalid={nidfederalid}
          nidid={nidid}
          source={source}
          sourceid={sourceid}
          partnerid={partnerid}
          link={link}
        />
      </Section>
    </Box>
  )
}

DamDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  alteredupstreammiles: PropTypes.number,
  annualflow: PropTypes.number,
  barrierownertype: PropTypes.number,
  basin: PropTypes.string,
  condition: PropTypes.number,
  construction: PropTypes.number,
  costlower: PropTypes.number,
  costmean: PropTypes.number,
  costupper: PropTypes.number,
  diversion: PropTypes.number,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  estimated: PropTypes.bool,
  excluded: PropTypes.bool,
  feasibilityclass: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  fercregulated: PropTypes.number,
  fishhabitatpartnership: PropTypes.string,
  flowstoocean: PropTypes.number,
  flowstogreatlakes: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  freeresilientdownstreammiles: PropTypes.number,
  hasnetwork: PropTypes.bool.isRequired,
  hazard: PropTypes.number,
  height: PropTypes.number,
  huc12: PropTypes.string,
  in_network_type: PropTypes.bool,
  intermittent: PropTypes.number,
  invasive: PropTypes.bool,
  landcover: PropTypes.number,
  link: PropTypes.string,
  lowheaddam: PropTypes.number,
  milestooutlet: PropTypes.number,
  nativeterritories: PropTypes.string,
  nidfederalid: PropTypes.string,
  nidid: PropTypes.string,
  onloop: PropTypes.bool,
  ownertype: PropTypes.number,
  partnerid: PropTypes.string,
  passability: PropTypes.number,
  passagefacility: PropTypes.number,
  percentresilient: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  purpose: PropTypes.number,
  recon: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  removed: PropTypes.bool,
  resilientupstreammiles: PropTypes.number,
  river: PropTypes.string,
  salmonidesu: PropTypes.string,
  sizeclasses: PropTypes.number,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  sourceid: PropTypes.string,
  stateregulated: PropTypes.number,
  statesgcnspp: PropTypes.number,
  storagevolume: PropTypes.number,
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
  unranked: PropTypes.bool,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  waterright: PropTypes.number,
  yearcompleted: PropTypes.number,
  yearremoved: PropTypes.number,
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

DamDetails.defaultProps = {
  alteredupstreammiles: 0,
  annualflow: null,
  barrierownertype: null,
  basin: null,
  condition: null,
  construction: null,
  costlower: 0,
  costmean: 0,
  costupper: 0,
  diversion: 0,
  ejtract: false,
  ejtribal: false,
  estimated: false,
  excluded: false,
  feasibilityclass: 0,
  fedregulatoryagency: null,
  fercregulated: null,
  fishhabitatpartnership: null,
  flowstoocean: 0,
  flowstogreatlakes: 0,
  freealtereddownstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  freeresilientdownstreammiles: 0,
  hazard: null,
  height: 0,
  huc12: null,
  in_network_type: false,
  intermittent: -1,
  invasive: false,
  landcover: null,
  link: null,
  lowheaddam: null,
  milestooutlet: 0,
  nativeterritories: null,
  nidfederalid: null,
  nidid: null,
  onloop: false,
  ownertype: null,
  partnerid: null,
  passability: null,
  passagefacility: null,
  percentresilient: 0,
  perennialupstreammiles: 0,
  purpose: null,
  recon: null,
  regionalsgcnspp: 0,
  removed: false,
  resilientupstreammiles: 0,
  river: null,
  salmonidesu: null,
  sizeclasses: null,
  snapped: false,
  source: null,
  sourceid: null,
  stateregulated: null,
  statesgcnspp: 0,
  storagevolume: null,
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
  unranked: false,
  waterbodykm2: -1,
  waterbodysizeclass: null,
  waterright: null,
  yearcompleted: 0,
  yearremoved: 0,
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

export default DamDetails

// print(',\n'.join(sorted([p.strip(',').strip(' ') for p in s.replace('\n','').split(',')])))
