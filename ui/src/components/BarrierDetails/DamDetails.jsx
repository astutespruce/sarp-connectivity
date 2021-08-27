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
} from '../../../config/constants'

import NetworkInfo from './NetworkInfo'

const { version: dataVersion } = siteMetadata

const DamDetails = ({
  sarpid,
  lat,
  lon,
  hasnetwork,
  excluded,
  height,
  nidid,
  source,
  year,
  construction,
  purpose,
  condition,
  passagefacility,
  river,
  intermittent,
  HUC8,
  HUC12,
  HUC8Name,
  HUC12Name,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
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
    }}
  >
    <Section title="Location">
      <Entry>
        {formatNumber(lat, 3)}
        &deg; N / {formatNumber(lon, 3)}
        &deg; E
      </Entry>

      {river && river !== '"' && river !== 'null' && river !== 'Unknown' ? (
        <Entry>
          <Field>River or stream:</Field> {river}
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
          <Paragraph variant="help">(HUC12: {HUC12})</Paragraph>
        </Entry>
      ) : null}

      {HUC8Name ? (
        <Entry>
          {HUC8Name} Subbasin{' '}
          <Paragraph variant="help">(HUC8: {HUC8})</Paragraph>
        </Entry>
      ) : null}

      {ownertype && ownertype > 0 && (
        <Entry>
          <Field>Conservation land type:</Field> {OWNERTYPE[ownertype]}
        </Entry>
      )}
    </Section>

    <Section title="Construction information">
      <Entry>
        <Field>Barrier type:</Field> dam
      </Entry>
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
              <Paragraph variant="help" sx={{ mt: '1rem' }}>
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
      {tespp > 0 ? (
        <>
          <Entry>
            <b>{tespp}</b> federally-listed threatened and endangered aquatic
            species have been found in the subwatershed containing this barrier.
          </Entry>
        </>
      ) : (
        <Entry>
          No federally-listed threatened and endangered aquatic species have
          been identified by available data sources for this subwatershed.
        </Entry>
      )}

      {statesgcnspp > 0 ? (
        <>
          <Entry>
            <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
            Conservation Need (SGCN) have been found in the subwatershed
            containing this barrier. These may include state-listed threatened
            and endangered species.
          </Entry>
        </>
      ) : (
        <Entry>
          No state-listed aquatic Species of Greatest Conservation Need (SGCN)
          have been identified by available data sources for this subwatershed.
        </Entry>
      )}

      {regionalsgcnspp > 0 ? (
        <>
          <Entry>
            <b>{regionalsgcnspp}</b> regionally-listed aquatic species of
            greatest conservation need have been found in the subwatershed
            containing this barrier.
          </Entry>
        </>
      ) : (
        <Entry>
          No regionally-listed aquatic species of greatest conservation need
          have been identified by available data sources for this subwatershed.
        </Entry>
      )}

      {tespp + statesgcnspp + regionalsgcnspp > 0 ? (
        <Paragraph variant="help" sx={{ mt: '1rem' }}>
          Note: species information is very incomplete. These species may or may
          not be directly impacted by this barrier.{' '}
          <a href="/sgcn" target="_blank">
            Read more.
          </a>
        </Paragraph>
      ) : null}
    </Section>

    <Section title="Feasibility & conservation benefit">
      {recon !== null ? (
        <Entry>{RECON[recon]}</Entry>
      ) : (
        <Entry>No feasibility information is available for this barrier.</Entry>
      )}

      {/* watershed priorities */}
      {huc8_usfs > 0 && (
        <Entry>
          Within USFS {HUC8_USFS[huc8_usfs]} priority watershed.{' '}
          <a href="/usfs_priority_watersheds" target="_blank">
            Read more.
          </a>
        </Entry>
      )}
      {huc8_coa > 0 && (
        <Entry>
          Within a SARP conservation opportunity area.{' '}
          <OutboundLink to="https://southeastaquatics.net/sarps-programs/usfws-nfhap-aquatic-habitat-restoration-program/conservation-opportunity-areas">
            Read more.
          </OutboundLink>
        </Entry>
      )}
      {huc8_sgcn > 0 && (
        <Entry>
          Within one of the top 10 watersheds in this state based on number of
          state-listed Species of Greatest Conservation Need.{' '}
          <a href="/sgcn" target="_blank">
            Read more.
          </a>
        </Entry>
      )}
    </Section>

    <Section title="Other information">
      <Entry>
        SARP ID: {sarpid} (data version: {dataVersion})
      </Entry>
      {!isEmptyString(nidid) ? (
        <Entry>
          National inventory of dams ID:{' '}
          <OutboundLink to="http://nid.usace.army.mil/cm_apex/f?p=838:12">
            {nidid}
          </OutboundLink>
        </Entry>
      ) : null}

      {!isEmptyString(source) ? <Entry>Source: {source}</Entry> : null}
    </Section>
  </Box>
)

DamDetails.propTypes = {
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
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passagefacility: PropTypes.number,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
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
  height: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
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
}

export default DamDetails
