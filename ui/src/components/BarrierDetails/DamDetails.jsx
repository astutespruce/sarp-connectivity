import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text, Paragraph } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'

import { siteMetadata } from '../../../gatsby-config'
import {
  SINUOSITY,
  DAM_CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  RECON,
  OWNERTYPE,
  HUC8_USFS,
} from '../../../config/constants'

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
  freeupstreammiles,
  freedownstreammiles,
  totalupstreammiles,
  totaldownstreammiles,
  sinuosityclass,
  landcover,
  sizeclasses,
}) => (
  <Box
    sx={{
      '&>div+div': {
        mt: '0.5rem',
        pt: '0.5rem',
        borderTop: '1px solid',
        borderTopColor: 'grey.2',
      },
    }}
  >
    <Box>
      <Text sx={{ fontWeight: 'bold' }}>Location</Text>
      <Box as="ul" sx={{ mt: '0.5rem' }}>
        <li>
          {formatNumber(lat, 3)}
          &deg; N / {formatNumber(lon, 3)}
          &deg; E
        </li>

        {river && river !== '"' && river !== 'null' && river !== 'Unknown' ? (
          <li>River or stream: {river}</li>
        ) : null}

        {intermittent ? (
          <li>Located on a reach that has intermittent or ephemeral flow</li>
        ) : null}

        {HUC12Name ? (
          <li>
            {HUC12Name} Subwatershed{' '}
            <Paragraph variant="help">(HUC12: {HUC12})</Paragraph>
          </li>
        ) : null}

        {HUC8Name ? (
          <li>
            {HUC8Name} Subbasin{' '}
            <Paragraph variant="help">(HUC8: {HUC8})</Paragraph>
          </li>
        ) : null}

        {ownertype && ownertype > 0 && (
          <li>Conservation land type: {OWNERTYPE[ownertype]}</li>
        )}
      </Box>
    </Box>

    <Box>
      <Text sx={{ fontWeight: 'bold' }}>Construction information</Text>
      <Box as="ul" sx={{ mt: '0.5rem' }}>
        <li>Barrier type: dam</li>
        {year > 0 ? <li>Constructed completed: {year}</li> : null}
        {height > 0 ? <li>Height: {height} feet</li> : null}
        {construction && CONSTRUCTION[construction] ? (
          <li>
            Construction material: {CONSTRUCTION[construction].toLowerCase()}
          </li>
        ) : null}
        {purpose && PURPOSE[purpose] ? (
          <li>Purpose: {PURPOSE[purpose].toLowerCase()}</li>
        ) : null}
        {condition && DAM_CONDITION[condition] ? (
          <li>
            Structural condition: {DAM_CONDITION[condition].toLowerCase()}
          </li>
        ) : null}

        {PASSAGEFACILITY[passagefacility] ? (
          <li>
            Passage facility type:{' '}
            {PASSAGEFACILITY[passagefacility].toLowerCase()}
          </li>
        ) : null}
      </Box>
    </Box>

    <Box>
      <Text sx={{ fontWeight: 'bold' }}>Functional network information</Text>

      <Box as="ul" sx={{ mt: '0.5rem' }}>
        {hasnetwork ? (
          <>
            <li>
              <b>
                {formatNumber(
                  Math.min(totalupstreammiles, freedownstreammiles)
                )}{' '}
                miles
              </b>{' '}
              could be gained by removing this barrier.
              <Box as="ul" sx={{ mt: '0.5rem' }}>
                <li>
                  {formatNumber(freeupstreammiles)} free-flowing miles upstream
                  <ul>
                    <li>
                      <b>{formatNumber(totalupstreammiles)} total miles</b> in
                      the upstream network
                    </li>
                  </ul>
                </li>

                <li>
                  <b>{formatNumber(freedownstreammiles)} free-flowing miles</b>{' '}
                  in the downstream network
                  <ul>
                    <li>
                      {formatNumber(totaldownstreammiles)} total miles in the
                      downstream network
                    </li>
                  </ul>
                </li>
              </Box>
            </li>
            <li>
              <b>{sizeclasses}</b> river size{' '}
              {sizeclasses === 1 ? 'class' : 'classes'} could be gained by
              removing this barrier
            </li>
            <li>
              <b>{formatNumber(landcover, 0)}%</b> of the upstream floodplain is
              composed of natural landcover
            </li>
            <li>
              The upstream network has <b>{SINUOSITY[sinuosityclass]}</b>{' '}
              sinuosity
            </li>
          </>
        ) : (
          <>
            {excluded ? (
              <li>
                This dam was excluded from the connectivity analysis based on
                field reconnaissance or manual review of aerial imagery.
              </li>
            ) : (
              <>
                <li>
                  This dam is off-network and has no functional network
                  information.
                </li>
                <Paragraph variant="help" sx={{ mt: '1rem' }}>
                  Not all dams could be correctly snapped to the aquatic network
                  for analysis. Please contact us to report an error or for
                  assistance interpreting these results.
                </Paragraph>
              </>
            )}
          </>
        )}
      </Box>
    </Box>

    <Box>
      <Text sx={{ fontWeight: 'bold' }}>Species information</Text>
      <Box as="ul" sx={{ mt: '0.5rem' }}>
        {tespp > 0 ? (
          <>
            <li>
              <b>{tespp}</b> federally-listed threatened and endangered aquatic
              species have been found in the subwatershed containing this
              barrier.
            </li>
          </>
        ) : (
          <li>
            No federally-listed threatened and endangered aquatic species have
            been identified by available data sources for this subwatershed.
          </li>
        )}

        {statesgcnspp > 0 ? (
          <>
            <li>
              <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
              Conservation Need (SGCN) have been found in the subwatershed
              containing this barrier. These may include state-listed threatened
              and endangered species.
            </li>
          </>
        ) : (
          <li>
            No state-listed aquatic Species of Greatest Conservation Need (SGCN)
            have been identified by available data sources for this
            subwatershed.
          </li>
        )}

        {regionalsgcnspp > 0 ? (
          <>
            <li>
              <b>{regionalsgcnspp}</b> regionally-listed aquatic species of
              greatest conservation need have been found in the subwatershed
              containing this barrier.
            </li>
          </>
        ) : (
          <li>
            No regionally-listed aquatic species of greatest conservation need
            have been identified by available data sources for this
            subwatershed.
          </li>
        )}

        {tespp + statesgcnspp + regionalsgcnspp > 0 ? (
          <Paragraph variant="help" sx={{ mt: '1rem' }}>
            Note: species information is very incomplete. These species may or
            may not be directly impacted by this barrier.{' '}
            <a href="/sgcn" target="_blank">
              Read more.
            </a>
          </Paragraph>
        ) : null}
      </Box>
    </Box>

    <Box>
      <Text sx={{ fontWeight: 'bold' }}>
        Feasibility & conservation benefit
      </Text>
      <Box as="ul" sx={{ mt: '0.5rem' }}>
        {recon !== null ? (
          <li>{RECON[recon]}</li>
        ) : (
          <li>No feasibility information is available for this barrier.</li>
        )}

        {/* watershed priorities */}
        {huc8_usfs > 0 && (
          <li>
            Within USFS {HUC8_USFS[huc8_usfs]} priority watershed.{' '}
            <a href="/usfs_priority_watersheds" target="_blank">
              Read more.
            </a>
          </li>
        )}
        {huc8_coa > 0 && (
          <li>
            Within a SARP conservation opportunity area.{' '}
            <OutboundLink to="https://southeastaquatics.net/sarps-programs/usfws-nfhap-aquatic-habitat-restoration-program/conservation-opportunity-areas">
              Read more.
            </OutboundLink>
          </li>
        )}
        {huc8_sgcn > 0 && (
          <li>
            Within one of the top 10 watersheds in this state based on number of
            state-listed Species of Greatest Conservation Need.{' '}
            <a href="/sgcn" target="_blank">
              Read more.
            </a>
          </li>
        )}
      </Box>
    </Box>

    <Box>
      <Text sx={{ fontWeight: 'bold' }}>Other information</Text>
      <Box as="ul" sx={{ mt: '0.5rem' }}>
        <li>
          SARP ID: {sarpid} (data version: {dataVersion})
        </li>
        {!isEmptyString(nidid) ? (
          <li>
            National inventory of dams ID:{' '}
            <OutboundLink to="http://nid.usace.army.mil/cm_apex/f?p=838:12">
              {nidid}
            </OutboundLink>
          </li>
        ) : null}

        {!isEmptyString(source) ? <li>Source: {source}</li> : null}
      </Box>
    </Box>
  </Box>
)

DamDetails.propTypes = {
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  excluded: PropTypes.bool,
  river: PropTypes.string,
  intermittent: PropTypes.bool,
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
  freeupstreammiles: PropTypes.number,
  totalupstreammiles: PropTypes.number,
  freedownstreammiles: PropTypes.number,
  totaldownstreammiles: PropTypes.number,
  sinuosityclass: PropTypes.number,
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
  intermittent: false,
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
  freeupstreammiles: null,
  totalupstreammiles: null,
  freedownstreammiles: null,
  totaldownstreammiles: null,
  sinuosityclass: null,
  landcover: null,
  sizeclasses: null,
}

export default DamDetails
