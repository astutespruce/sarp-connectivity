import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { Entry, Field, Section } from 'components/Sidebar'

import {
  siteMetadata,
  CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  RECON,
  PASSABILITY,
} from 'config'

import DiadromousInfo from './DiadromousInfo'
import IDInfo from './IDInfo'
import LocationInfo from './LocationInfo'
import NetworkInfo from './NetworkInfo'
import NoNetworkInfo from './NoNetworkInfo'
import SpeciesInfo from './SpeciesInfo'

const { version: dataVersion } = siteMetadata

const DamDetails = ({
  barrierType,
  networkType,
  sarpid,
  hasnetwork,
  excluded,
  onloop,
  unsnapped,
  height,
  nidid,
  source,
  link,
  estimated,
  yearcompleted,
  construction,
  diversion,
  nostructure,
  purpose,
  condition,
  passability,
  removed,
  yearremoved,
  lowheaddam,
  passagefacility,
  river,
  streamorder,
  streamsizeclass,
  waterbodykm2,
  waterbodysizeclass,
  intermittent,
  HUC12,
  HUC8Name,
  HUC12Name,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  recon,
  ownertype,
  barrierownertype,
  disadvantagedcommunity,
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
  invasive,
  unranked,
  flowstoocean,
  milestooutlet,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
}) => {
  const isLowheadDam = lowheaddam !== null && lowheaddam >= 1
  const isDiversion = diversion !== null && diversion >= 1
  const isUnspecifiedType = !(isLowheadDam || isDiversion || invasive)

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
                {nostructure === 1 ? (
                  <Text sx={{ fontSize: 0, color: 'grey.8' }}>
                    (no associated barrier structure)
                  </Text>
                ) : null}
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
                  : '(removed)'}
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
          HUC8Name={HUC8Name}
          HUC12Name={HUC12Name}
          HUC12={HUC12}
          ownertype={ownertype}
          barrierownertype={barrierownertype}
          disadvantagedcommunity={disadvantagedcommunity}
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
          <Entry>
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
          />
        ) : (
          <NoNetworkInfo
            barrierType={barrierType}
            unsnapped={unsnapped}
            excluded={excluded}
            onloop={onloop}
            diversion={diversion}
            nostructure={nostructure}
          />
        )}
      </Section>

      {flowstoocean && milestooutlet < 500 ? (
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

      <Section title="Feasibility & conservation benefit">
        {recon !== null && recon >= 0 ? (
          <Entry>{RECON[recon]}</Entry>
        ) : (
          <Entry>No feasibility information is available for this dam.</Entry>
        )}
      </Section>

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
  hasnetwork: PropTypes.number.isRequired,
  excluded: PropTypes.number,
  onloop: PropTypes.number,
  unsnapped: PropTypes.number,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  HUC12: PropTypes.string,
  HUC8Name: PropTypes.string,
  HUC12Name: PropTypes.string,
  height: PropTypes.number,
  yearcompleted: PropTypes.number,
  nidid: PropTypes.string,
  source: PropTypes.string,
  link: PropTypes.string,
  estimated: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passability: PropTypes.number,
  removed: PropTypes.bool,
  yearremoved: PropTypes.number,
  passagefacility: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
  recon: PropTypes.number,
  ownertype: PropTypes.number,
  barrierownertype: PropTypes.number,
  disadvantagedcommunity: PropTypes.string,
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
  diversion: PropTypes.number,
  nostructure: PropTypes.number,
  lowheaddam: PropTypes.number,
  streamorder: PropTypes.number,
  streamsizeclass: PropTypes.string,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
  invasive: PropTypes.number,
  unranked: PropTypes.number,
  flowstoocean: PropTypes.number,
  milestooutlet: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
}

DamDetails.defaultProps = {
  HUC12: null,
  HUC8Name: null,
  HUC12Name: null,
  excluded: 0,
  onloop: 0,
  unsnapped: 0,
  river: null,
  intermittent: -1,
  nidid: null,
  source: null,
  link: null,
  estimated: 0,
  height: 0,
  yearcompleted: 0,
  construction: null,
  purpose: null,
  condition: null,
  passability: null,
  removed: false,
  yearremoved: 0,
  passagefacility: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
  recon: null,
  ownertype: null,
  barrierownertype: null,
  disadvantagedcommunity: null,
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
  diversion: 0,
  nostructure: 0,
  lowheaddam: null,
  streamorder: 0,
  streamsizeclass: null,
  waterbodykm2: -1,
  waterbodysizeclass: null,
  invasive: 0,
  unranked: 0,
  flowstoocean: 0,
  milestooutlet: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
}

export default DamDetails
