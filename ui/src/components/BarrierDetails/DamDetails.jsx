import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text, Paragraph } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { OutboundLink } from 'components/Link'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import { siteMetadata } from '../../../gatsby-config'
import {
  DAM_CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  RECON,
  OWNERTYPE,
  HUC8_USFS,
  WATERBODY_SIZECLASS,
} from '../../../config/constants'

import NetworkInfo from './NetworkInfo'

const { version: dataVersion } = siteMetadata

const DamDetails = ({
  barrierType,
  sarpid,
  lat,
  lon,
  hasnetwork,
  excluded,
  height,
  nidid,
  source,
  estimated,
  year,
  construction,
  diversion,
  purpose,
  condition,
  lowheaddam,
  passagefacility,
  river,
  waterbodykm2,
  waterbodysizeclass,
  intermittent,
  HUC8,
  HUC12,
  HUC8Name,
  HUC12Name,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  recon,
  ownertype,
  huc8_usfs,
  huc8_coa,
  huc8_sgcn,
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
}) => (
  <Box
    sx={{
      mt: '-1rem',
      mx: '-1rem',
      fontSize: 1,
    }}
  >
    <Section title="Location">
      <Entry>
        {estimated === 1 ? 'Estimated dam' : 'Dam'} at {formatNumber(lat, 5)},{' '}
        {formatNumber(lon, 5)} (&deg;N, &deg;E)
        {estimated === 1 ? (
          <Paragraph variant="help" sx={{ fontSize: 0, mt: '0.5em' }}>
            Dam is estimated from other data sources and may be incorrect;
            please{' '}
            <a
              href={`mailto:Kat@southeastaquatics.net?subject=Problem with Estimated Dam ${sarpid} (data version: ${dataVersion})`}
            >
              let us know
            </a>
          </Paragraph>
        ) : null}
      </Entry>

      {river && river !== '"' && river !== 'null' && river !== 'Unknown' ? (
        <Entry>
          <Field>River or stream:</Field> {river}
        </Entry>
      ) : null}

      {waterbodysizeclass >= 0 ? (
        <Entry>
          <Field>Size of associated pond or lake:</Field>{' '}
          {waterbodykm2 > 0.1
            ? `${formatNumber(waterbodykm2, 2)} k`
            : `${formatNumber(waterbodykm2 * 1e6)} `}
          m<sup>2</sup> (
          {WATERBODY_SIZECLASS[waterbodysizeclass].split(' (')[0].toLowerCase()}
          )
        </Entry>
      ) : null}

      {intermittent === 1 ? (
        <Entry>
          Located on a reach that has intermittent or ephemeral flow
        </Entry>
      ) : null}

      {HUC12Name ? (
        <Entry>
          {HUC12Name} Subwatershed{' '}
          <Paragraph variant="help" sx={{ fontSize: 0 }}>
            HUC12: {HUC12}
          </Paragraph>
        </Entry>
      ) : null}

      {HUC8Name ? (
        <Entry>
          {HUC8Name} Subbasin{' '}
          <Paragraph variant="help" sx={{ fontSize: 0 }}>
            HUC8: {HUC8}
          </Paragraph>
        </Entry>
      ) : null}

      {ownertype && ownertype > 0 ? (
        <Entry>
          <Field>Conservation land type:</Field> {OWNERTYPE[ownertype]}
        </Entry>
      ) : null}
    </Section>

    <Section title="Construction information">
      {year > 0 ? (
        <Entry>
          <Field>Constructed completed:</Field> {year}
        </Entry>
      ) : null}
      {height > 0 ? (
        <Entry>
          <Field>Height:</Field> {height} feet
        </Entry>
      ) : null}
      {construction && CONSTRUCTION[construction] ? (
        <Entry>
          <Field>Construction material:</Field>{' '}
          {CONSTRUCTION[construction].toLowerCase()}
        </Entry>
      ) : null}
      {lowheaddam >= 1 ? (
        <Entry>This is {lowheaddam === 2 ? 'likely' : ''} a lowhead dam</Entry>
      ) : null}
      {diversion === 1 ? (
        <Entry>
          <Field>Diversion:</Field> this dam is a diversion structure
        </Entry>
      ) : null}
      {purpose && PURPOSE[purpose] ? (
        <Entry>
          <Field>Purpose:</Field> {PURPOSE[purpose].toLowerCase()}
        </Entry>
      ) : null}
      {condition && DAM_CONDITION[condition] ? (
        <Entry>
          <Field>Structural condition:</Field>{' '}
          {DAM_CONDITION[condition].toLowerCase()}
        </Entry>
      ) : null}

      {PASSAGEFACILITY[passagefacility] ? (
        <Entry>
          <Field>Passage facility type:</Field>{' '}
          {PASSAGEFACILITY[passagefacility].toLowerCase()}
        </Entry>
      ) : null}
    </Section>

    <Section title="Functional network information">
      {hasnetwork ? (
        <NetworkInfo
          barrierType={barrierType}
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
        />
      ) : (
        <>
          {excluded ? (
            <Entry>
              This dam was excluded from the connectivity analysis based on
              field reconnaissance or manual review of aerial imagery.
            </Entry>
          ) : (
            <Entry>
              <Text>
                This dam is off-network and has no functional network
                information.
              </Text>
              <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
                Not all dams could be correctly snapped to the aquatic network
                for analysis. Please contact us to report an error or for
                assistance interpreting these results.
              </Paragraph>
            </Entry>
          )}
        </>
      )}
    </Section>

    <Section title="Species information">
      <Text sx={{ my: '0.5rem', mr: '0.5rem' }}>
        Data sources in the subwatershed containing this dam have recorded:
      </Text>
      <Box as="ul">
        <li>
          <b>{tespp}</b> federally-listed threatened and endangered aquatic
          species
        </li>
        <li>
          <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
          Conservation Need (SGCN), which include state-listed threatened and
          endangered species
        </li>
        <li>
          <b>{regionalsgcnspp}</b> regionally-listed aquatic Species of Greatest
          Conservation Need
        </li>
        <li>{trout ? 'One or more trout species' : 'No trout species'}</li>
      </Box>

      <Paragraph variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
        Note: species information is very incomplete. These species may or may
        not be directly impacted by this dam.{' '}
        <a href="/sgcn" target="_blank">
          Read more.
        </a>
      </Paragraph>
    </Section>

    <Section title="Feasibility & conservation benefit">
      {recon !== null ? (
        <Entry>{RECON[recon]}</Entry>
      ) : (
        <Entry>No feasibility information is available for this dam.</Entry>
      )}

      {/* watershed priorities */}
      {huc8_usfs > 0 ? (
        <Entry>
          Within USFS {HUC8_USFS[huc8_usfs]} priority watershed.{' '}
          <a href="/usfs_priority_watersheds" target="_blank">
            Read more.
          </a>
        </Entry>
      ) : null}
      {huc8_coa > 0 ? (
        <Entry>
          Within a SARP conservation opportunity area.{' '}
          <OutboundLink to="https://southeastaquatics.net/sarps-programs/usfws-nfhap-aquatic-habitat-restoration-program/conservation-opportunity-areas">
            Read more.
          </OutboundLink>
        </Entry>
      ) : null}
      {huc8_sgcn > 0 ? (
        <Entry>
          Within one of the top 10 watersheds in this state based on number of
          state-listed Species of Greatest Conservation Need.{' '}
          <a href="/sgcn" target="_blank">
            Read more.
          </a>
        </Entry>
      ) : null}
    </Section>

    <Section title="Other information">
      <Entry>
        <Field>SARP ID:</Field> {sarpid}
      </Entry>
      {!isEmptyString(nidid) ? (
        <Entry>
          <Field>National inventory of dams ID:</Field>{' '}
          <OutboundLink to="http://nid.usace.army.mil/cm_apex/f?p=838:12">
            {nidid}
          </OutboundLink>
        </Entry>
      ) : null}

      {!isEmptyString(source) ? (
        <Entry>
          <Field>Source:</Field> {source}
        </Entry>
      ) : null}
    </Section>
  </Box>
)

DamDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  river: PropTypes.string,
  intermittent: PropTypes.number,
  HUC8: PropTypes.string,
  HUC12: PropTypes.string,
  HUC8Name: PropTypes.string,
  HUC12Name: PropTypes.string,
  height: PropTypes.number,
  year: PropTypes.number,
  nidid: PropTypes.string,
  source: PropTypes.string,
  estimated: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passagefacility: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  recon: PropTypes.number,
  ownertype: PropTypes.number,
  huc8_usfs: PropTypes.number,
  huc8_coa: PropTypes.number,
  huc8_sgcn: PropTypes.number,
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
  lowheaddam: PropTypes.number,
  waterbodykm2: PropTypes.number,
  waterbodysizeclass: PropTypes.number,
}

DamDetails.defaultProps = {
  HUC8: null,
  HUC12: null,
  HUC8Name: null,
  HUC12Name: null,
  excluded: false,
  river: null,
  intermittent: -1,
  nidid: null,
  source: null,
  estimated: 0,
  height: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  recon: 0,
  ownertype: null,
  huc8_usfs: 0,
  huc8_coa: 0,
  huc8_sgcn: 0,
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
  lowheaddam: -1,
  waterbodykm2: -1,
  waterbodysizeclass: -1,
}

export default DamDetails
