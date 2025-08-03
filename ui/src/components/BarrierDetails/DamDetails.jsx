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
import FunctionalNetworkInfo from './FunctionalNetworkInfo'
import MainstemNetworkInfo from './MainstemNetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesWatershedPresenceInfo from './SpeciesWatershedPresenceInfo'
import SpeciesHabitatInfo from './SpeciesHabitatInfo'
import { HabitatPropTypeStub, HabitatDefaultPropStub } from './proptypes'

const { version: dataVersion } = siteMetadata

const DamDetails = ({
  barrierType,
  networkType,
  sarpid,
  lat,
  lon,
  alteredupstreammiles,
  alteredmainstemupstreammiles,
  annualflow,
  barrierownertype,
  basin,
  canal,
  coldupstreammiles,
  condition,
  construction,
  congressionaldistrict,
  costlower,
  costmean,
  costupper,
  diadromoushabitat,
  diversion,
  ejtract,
  ejtribal,
  estimated,
  excluded,
  fatality,
  feasibilityclass,
  fedregulatoryagency,
  fercregulated,
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
  hazard,
  height,
  huc12,
  in_network_type,
  intermittent,
  invasive,
  landcover,
  sourcelink,
  lowheaddam,
  mainstemsizeclasses,
  milestooutlet,
  nativeterritories,
  nidfederalid,
  nidid,
  nrcsdam,
  onloop,
  ownertype,
  partnerid,
  passability,
  passagefacility,
  percentcold,
  percentresilient,
  perennialupstreammiles,
  perennialmainstemupstreammiles,
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
  totalmainstemupstreammiles,
  trout,
  unalteredupstreammiles,
  unalteredmainstemupstreammiles,
  unranked,
  unalteredwaterbodyacres,
  unalteredwetlandacres,
  waterbodyacres,
  waterbodysizeclass,
  waterright,
  wilderness,
  wildscenicriver,
  yearcompleted,
  yearremoved,
  yearsurveyed,
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
          congressionaldistrict={congressionaldistrict}
          ownertype={ownertype}
          barrierownertype={barrierownertype}
          fercregulated={fercregulated}
          stateregulated={stateregulated}
          nrcsdam={nrcsdam}
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
          canal={canal}
          storagevolume={storagevolume}
          streamorder={streamorder}
          streamsizeclass={streamsizeclass}
          waterbodysizeclass={waterbodysizeclass}
          waterbodyacres={waterbodyacres}
          wilderness={wilderness}
          wildscenicriver={wildscenicriver}
          fatality={fatality}
          yearsurveyed={yearsurveyed}
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
          <FunctionalNetworkInfo
            barrierType={barrierType}
            networkType={networkType}
            // regular network
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
            waterbodysizeclass={waterbodysizeclass}
            waterbodyacres={waterbodyacres}
            intermittent={intermittent}
            invasive={invasive}
            unranked={unranked}
            removed={removed}
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
            diversion={diversion}
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
          />
        </Section>
      ) : null}

      {hasnetwork && totalmainstemupstreammiles > 0 ? (
        <Section title="Mainstem network information">
          <MainstemNetworkInfo
            barrierType={barrierType}
            networkType={networkType}
            removed={removed}
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
          sourcelink={sourcelink}
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
  alteredmainstemupstreammiles: PropTypes.number,
  annualflow: PropTypes.number,
  barrierownertype: PropTypes.number,
  basin: PropTypes.string,
  canal: PropTypes.number,
  coldupstreammiles: PropTypes.number,
  condition: PropTypes.number,
  congressionaldistrict: PropTypes.string,
  construction: PropTypes.number,
  costlower: PropTypes.number,
  costmean: PropTypes.number,
  costupper: PropTypes.number,
  diadromoushabitat: PropTypes.number,
  diversion: PropTypes.number,
  ejtract: PropTypes.bool,
  ejtribal: PropTypes.bool,
  estimated: PropTypes.bool,
  excluded: PropTypes.bool,
  fatality: PropTypes.number,
  feasibilityclass: PropTypes.number,
  fedregulatoryagency: PropTypes.string,
  fercregulated: PropTypes.number,
  fishhabitatpartnership: PropTypes.string,
  flowstoocean: PropTypes.number,
  flowstogreatlakes: PropTypes.number,
  freealtereddownstreammiles: PropTypes.number,
  freealteredlineardownstreammiles: PropTypes.number,
  freecolddownstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  freelineardownstreammiles: PropTypes.number,
  freeperennialdownstreammiles: PropTypes.number,
  freeperenniallineardownstreammiles: PropTypes.number,
  freeunaltereddownstreammiles: PropTypes.number,
  freeunalteredlineardownstreammiles: PropTypes.number,
  freeresilientdownstreammiles: PropTypes.number,
  hasnetwork: PropTypes.bool.isRequired,
  hazard: PropTypes.number,
  height: PropTypes.number,
  huc12: PropTypes.string,
  in_network_type: PropTypes.bool,
  intermittent: PropTypes.number,
  invasive: PropTypes.bool,
  landcover: PropTypes.number,
  sourcelink: PropTypes.string,
  lowheaddam: PropTypes.number,
  mainstemsizeclasses: PropTypes.number,
  milestooutlet: PropTypes.number,
  nativeterritories: PropTypes.string,
  nidfederalid: PropTypes.string,
  nidid: PropTypes.string,
  nrcsdam: PropTypes.number,
  onloop: PropTypes.bool,
  ownertype: PropTypes.number,
  partnerid: PropTypes.string,
  passability: PropTypes.number,
  passagefacility: PropTypes.number,
  percentcold: PropTypes.number,
  percentresilient: PropTypes.number,
  perennialupstreammiles: PropTypes.number,
  perennialmainstemupstreammiles: PropTypes.number,
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
  totalmainstemupstreammiles: PropTypes.number,
  trout: PropTypes.string,
  unalteredupstreammiles: PropTypes.number,
  unalteredmainstemupstreammiles: PropTypes.number,
  unranked: PropTypes.bool,
  unalteredwaterbodyacres: PropTypes.number,
  unalteredwetlandacres: PropTypes.number,
  waterbodyacres: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  waterright: PropTypes.number,
  wilderness: PropTypes.number,
  wildscenicriver: PropTypes.number,
  yearcompleted: PropTypes.number,
  yearremoved: PropTypes.number,
  yearsurveyed: PropTypes.number,
  invasivenetwork: PropTypes.number,
  ...HabitatPropTypeStub,
}

DamDetails.defaultProps = {
  alteredupstreammiles: 0,
  alteredmainstemupstreammiles: 0,
  annualflow: null,
  barrierownertype: null,
  basin: null,
  canal: 0,
  coldupstreammiles: 0,
  condition: null,
  congressionaldistrict: null,
  construction: null,
  costlower: 0,
  costmean: 0,
  costupper: 0,
  diadromoushabitat: 0,
  diversion: 0,
  fatality: 0,
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
  freealteredlineardownstreammiles: 0,
  freecolddownstreammiles: 0,
  freedownstreammiles: 0,
  freelineardownstreammiles: 0,
  freeperennialdownstreammiles: 0,
  freeperenniallineardownstreammiles: 0,
  freeunaltereddownstreammiles: 0,
  freeunalteredlineardownstreammiles: 0,
  freeresilientdownstreammiles: 0,
  hazard: null,
  height: 0,
  huc12: null,
  in_network_type: false,
  intermittent: 0,
  invasive: false,
  landcover: null,
  sourcelink: null,
  lowheaddam: null,
  mainstemsizeclasses: 0,
  milestooutlet: 0,
  nativeterritories: null,
  nidfederalid: null,
  nidid: null,
  nrcsdam: null,
  onloop: false,
  ownertype: null,
  partnerid: null,
  passability: null,
  passagefacility: null,
  percentcold: 0,
  percentresilient: 0,
  perennialupstreammiles: 0,
  perennialmainstemupstreammiles: 0,
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
  totalmainstemupstreammiles: 0,
  trout: null,
  unalteredupstreammiles: 0,
  unalteredmainstemupstreammiles: 0,
  unranked: false,
  unalteredwaterbodyacres: 0,
  unalteredwetlandacres: 0,
  waterbodyacres: -1,
  waterbodysizeclass: null,
  waterright: null,
  wilderness: null,
  wildscenicriver: null,
  yearcompleted: 0,
  yearremoved: 0,
  yearsurveyed: 0,
  invasivenetwork: 0,
  ...HabitatDefaultPropStub,
}

export default DamDetails

// print(',\n'.join(sorted([p.strip(',').strip(' ') for p in s.replace('\n','').split(',')])))
