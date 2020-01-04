import React from 'react'
import PropTypes from 'prop-types'

import { HelpText } from 'components/Text'

import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'
import { Section, SectionHeader, List } from './styles'

import { siteMetadata } from '../../../gatsby-config'
import {
  SINUOSITY,
  DAM_CONDITION,
  CONSTRUCTION,
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
  height,
  nidid,
  source,
  year,
  construction,
  purpose,
  condition,
  river,
  basin,
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
}) => {
  return (
    <div>
      <Section>
        <SectionHeader>Location</SectionHeader>
        <List>
          <li>
            {formatNumber(lat, 3)}
            &deg; N / {formatNumber(lon, 3)}
            &deg; E
          </li>
          <li>
            {river && river !== '"' && river !== 'null' && river !== 'Unknown'
              ? `${river}, `
              : null}
            {basin} Basin
          </li>
          {ownertype && ownertype > 0 && (
            <li>Conservation land type: {OWNERTYPE[ownertype]}</li>
          )}
        </List>
      </Section>

      <Section>
        <SectionHeader>Construction information</SectionHeader>
        <List>
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
        </List>
      </Section>

      <Section>
        <SectionHeader>Functional network information</SectionHeader>

        <List>
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
                <List style={{ marginTop: '0.5rem' }}>
                  <li>
                    {formatNumber(freeupstreammiles)} free-flowing miles
                    upstream
                    <ul>
                      <li>
                        <b>{formatNumber(totalupstreammiles)} total miles</b> in
                        the upstream network
                      </li>
                    </ul>
                  </li>

                  <li>
                    <b>
                      {formatNumber(freedownstreammiles)} free-flowing miles
                    </b>{' '}
                    in the downstream network
                    <ul>
                      <li>
                        {formatNumber(totaldownstreammiles)} total miles in the
                        downstream network
                      </li>
                    </ul>
                  </li>
                </List>
              </li>
              <li>
                <b>{sizeclasses}</b> river size{' '}
                {sizeclasses === 1 ? 'class' : 'classes'} could be gained by
                removing this barrier
              </li>
              <li>
                <b>{formatNumber(landcover, 0)}%</b> of the upstream floodplain
                is composed of natural landcover
              </li>
              <li>
                The upstream network has <b>{SINUOSITY[sinuosityclass]}</b>{' '}
                sinuosity
              </li>
            </>
          ) : (
            <li>
              This barrier is off-network and has no functional network
              information.
            </li>
          )}
        </List>
      </Section>

      <Section>
        <SectionHeader>Species information</SectionHeader>
        <List>
          {tespp > 0 ? (
            <>
              <li>
                <b>{tespp}</b> federally-listed threatened and endangered
                aquatic species have been found in the subwatershed containing
                this barrier.
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
                <b>{statesgcnspp}</b> state-listed aquatic species of greatest
                conservation need have been found in the subwatershed containing
                this barrier. These may include state-listed threatened and
                endangered species.
              </li>
            </>
          ) : (
            <li>
              No state-listed aquatic species of greatest conservation need have
              been identified by available data sources for this subwatershed.
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
            <HelpText mt="1rem" fontSize="smaller">
              Note: species information is very incomplete. These species may or
              may not be directly impacted by this barrier.
            </HelpText>
          ) : null}
        </List>
      </Section>

      <Section>
        <SectionHeader>Feasibility & Conservation Benefit</SectionHeader>
        <List>
          {recon !== null ? (
            <li>{RECON[recon]}</li>
          ) : (
            <li>No feasibility information is available for this barrier.</li>
          )}

          {/* watershed priorities */}
          {huc8_usfs > 0 && <li>USFS watershed priority: {HUC8_USFS[usfs]}</li>}
          {huc8_coa > 0 && <li>Within a SARP conservation opportunity area</li>}
          {huc8_sgcn > 0 && (
            <li>
              Watersheds with most Species of Greatest Conservation Need per
              state
            </li>
          )}
        </List>
      </Section>

      <Section>
        <SectionHeader>Other information</SectionHeader>
        <List>
          <li>
            SARP ID: {sarpid} (data version: {dataVersion})
          </li>
          {!isEmptyString(nidid) ? (
            <li>
              National inventory of dams ID:{' '}
              <a
                href="http://nid.usace.army.mil/cm_apex/f?p=838:12"
                target="_blank"
                rel="noopener noreferrer"
              >
                {nidid}
              </a>
            </li>
          ) : null}

          {!isEmptyString(source) ? <li>Source: {source}</li> : null}
        </List>
      </Section>
    </div>
  )
}

DamDetails.propTypes = {
  id: PropTypes.number.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  river: PropTypes.string,
  basin: PropTypes.string.isRequired,
  height: PropTypes.number,
  year: PropTypes.number,
  nidid: PropTypes.string,
  source: PropTypes.string,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
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
  river: null,
  nidid: null,
  source: null,
  height: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
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
