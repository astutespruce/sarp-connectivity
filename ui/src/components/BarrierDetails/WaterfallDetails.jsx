import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph, Text } from 'theme-ui'

import { Entry, Field, Section } from 'components/Sidebar'
import { OutboundLink } from 'components/Link'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import { OWNERTYPE, HUC8_USFS } from '../../../config/constants'

import NetworkInfo from './NetworkInfo'

const WaterfallDetails = ({
  barrierType,
  lat,
  lon,
  source,
  hasnetwork,
  excluded,
  stream,
  intermittent,
  HUC8,
  HUC12,
  HUC8Name,
  HUC12Name,
  falltype,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
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
        Waterfall at {formatNumber(lat, 3)}
        &deg; N, {formatNumber(lon, 3)}
        &deg; E
      </Entry>
      {!isEmptyString(stream) ? (
        <Entry>
          <Field>River or stream:</Field> {stream}
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

      {ownertype && ownertype > 0 ? (
        <Entry>
          <Field>Conservation land type:</Field> {OWNERTYPE[ownertype]}
        </Entry>
      ) : null}
    </Section>

    {falltype && !isEmptyString(falltype) ? (
      <Section title="Barrier information">
        <Entry>
          <Field>Waterfall type:</Field> {falltype}
        </Entry>
      </Section>
    ) : null}

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
              This waterfall was excluded from the connectivity analysis based
              on field reconnaissance or manual review of aerial imagery.
            </Entry>
          ) : (
            <Entry>
              <Text>
                This waterfall is off-network and has no functional network
                information.
              </Text>
              <Paragraph variant="help" sx={{ mt: '1rem' }}>
                Not all barriers could be correctly snapped to the aquatic
                network for analysis. Please contact us to report an error or
                for assistance interpreting these results.
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
            species have been found in the subwatershed containing this
            waterfall.
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
            <b>{statesgcnspp}</b> state-listed aquatic species of greatest
            conservation need have been found in the subwatershed containing
            this waterfall. These may include state-listed threatened and
            endangered species.
          </Entry>
        </>
      ) : (
        <Entry>
          No state-listed aquatic species of greatest conservation need have
          been identified by available data sources for this subwatershed.
        </Entry>
      )}

      {regionalsgcnspp > 0 ? (
        <>
          <Entry>
            <b>{regionalsgcnspp}</b> regionally-listed aquatic Species of
            Greatest Conservation Need (SGCN) have been found in the
            subwatershed containing this waterfall.
          </Entry>
        </>
      ) : (
        <Entry>
          No regionally-listed aquatic Species of Greatest Conservation Need
          (SGCN) have been identified by available data sources for this
          subwatershed.
        </Entry>
      )}

      <Paragraph variant="help" sx={{ mt: '1rem' }}>
        Note: species information is very incomplete. These species may or may
        not be directly impacted by this waterfall.{' '}
        <a href="/sgcn" target="_blank">
          Read more.
        </a>
      </Paragraph>
    </Section>

    {huc8_usfs + huc8_coa + huc8_sgcn > 0 ? (
      <Section title="Feasibility & conservation benefit">
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
    ) : null}

    {!isEmptyString(source) ? (
      <Section title="Other information">
        {!isEmptyString(source) ? (
          <Entry>
            <Field>Source:</Field> {source}
          </Entry>
        ) : null}
      </Section>
    ) : null}
  </Box>
)

WaterfallDetails.propTypes = {
  barrierType: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  source: PropTypes.string,
  stream: PropTypes.string,
  intermittent: PropTypes.number,
  HUC8: PropTypes.string,
  HUC12: PropTypes.string,
  HUC8Name: PropTypes.string,
  HUC12Name: PropTypes.string,
  falltype: PropTypes.string,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
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

WaterfallDetails.defaultProps = {
  HUC8: null,
  HUC12: null,
  HUC8Name: null,
  HUC12Name: null,
  excluded: false,
  source: null,
  stream: null,
  intermittent: false,
  falltype: null,
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
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

export default WaterfallDetails