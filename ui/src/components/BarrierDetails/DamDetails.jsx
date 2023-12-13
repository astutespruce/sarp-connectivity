import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { extractHabitat } from 'components/Data/Habitat'
import { Entry, Field, Section } from 'components/Sidebar'

import {
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

  alteredupstreammiles,
  barrierownertype,
  basin,
  condition,
  construction,
  diversion,
  ejtract,
  ejtribal,
  estimated,
  excluded,
  feasibilityclass,
  fercregulated,
  flowstoocean,
  freealtereddownstreammiles,
  freedownstreammiles,
  freeperennialdownstreammiles,
  freeunaltereddownstreammiles,
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
  nidid,
  onloop,
  ownertype,
  passability,
  passagefacility,
  perennialupstreammiles,
  purpose,
  recon,
  regionalsgcnspp,
  removed,
  river,
  salmonidesu,
  sizeclasses,
  snapped,
  source,
  stateregulated,
  statesgcnspp,
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
  ...props // includes species habitat fields selected dynamically
}) => {
  const isLowheadDam = lowheaddam !== null && lowheaddam >= 1
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
            {removed ? (
              <>
                <br />
                {yearremoved !== null && yearremoved > 0
                  ? `(removed in ${yearremoved})`
                  : '(removed / year unknown)'}
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
          reachName={river}
          basin={basin}
          subwatershed={subwatershed}
          huc12={huc12}
          ownertype={ownertype}
          barrierownertype={barrierownertype}
          fercregulated={fercregulated}
          stateregulated={stateregulated}
          waterright={waterright}
          // disadvantagedcommunity={disadvantagedcommunity}
          ejtract={ejtract}
          ejtribal={ejtribal}
          intermittent={intermittent}
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

        {passability !== null ? (
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
            freedownstreammiles={freedownstreammiles}
            freeperennialdownstreammiles={freeperennialdownstreammiles}
            freealtereddownstreammiles={freealtereddownstreammiles}
            freeunaltereddownstreammiles={freeunaltereddownstreammiles}
            sizeclasses={sizeclasses}
            landcover={landcover}
            waterbodysizeclass={waterbodysizeclass}
            waterbodykm2={waterbodykm2}
            intermittent={intermittent}
            invasive={invasive}
            unranked={unranked}
            removed={removed}
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

      {feasibilityclass && feasibilityclass <= 10 ? (
        <Section title="Feasibility & conservation benefit">
          <Entry>
            <Field label="Feasibility" isUnknown={feasibilityclass <= 1}>
              {FEASIBILITYCLASS[feasibilityclass]}
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

      <Section title="Other information">
        <IDInfo sarpid={sarpid} nidid={nidid} source={source} link={link} />
      </Section>
    </Box>
  )
}

DamDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,

  alteredupstreammiles: PropTypes.number,
  barrierownertype: PropTypes.number,
  basin: PropTypes.string,
  condition: PropTypes.number,
  construction: PropTypes.number,
  diversion: PropTypes.number,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  estimated: PropTypes.bool,
  excluded: PropTypes.bool,
  feasibilityclass: PropTypes.number,
  fercregulated: PropTypes.number,
  flowstoocean: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
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
  nidid: PropTypes.string,
  onloop: PropTypes.bool,
  ownertype: PropTypes.number,
  passability: PropTypes.number,
  passagefacility: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  purpose: PropTypes.number,
  recon: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  removed: PropTypes.bool,
  river: PropTypes.string,
  salmonidesu: PropTypes.string,
  sizeclasses: PropTypes.number,
  snapped: PropTypes.bool,
  source: PropTypes.string,
  stateregulated: PropTypes.number,
  statesgcnspp: PropTypes.number,
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
  barrierownertype: null,
  basin: null,
  condition: null,
  construction: null,
  diversion: 0,
  ejtract: false,
  ejtribal: false,
  estimated: false,
  excluded: false,
  feasibilityclass: 0,
  fercregulated: null,
  flowstoocean: 0,
  freealtereddownstreammiles: 0,
  freedownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
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
  nidid: null,
  onloop: false,
  ownertype: null,
  passability: null,
  passagefacility: null,
  perennialupstreammiles: 0,
  purpose: null,
  recon: null,
  regionalsgcnspp: 0,
  removed: false,
  river: null,
  salmonidesu: null,
  sizeclasses: null,
  snapped: false,
  source: null,
  stateregulated: null,
  statesgcnspp: 0,
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
