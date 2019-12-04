import React from 'react'
import PropTypes from 'prop-types'

import { formatNumber } from 'util/format'
import { isEmptyString } from 'util/string'
import { Section, SectionHeader, List } from './styles'

import { siteMetadata } from '../../../gatsby-config'
import {
  SINUOSITY,
  BARRIER_SEVERITY,
  OWNERTYPE,
} from '../../../config/constants'

const { version: dataVersion } = siteMetadata

const BarrierDetails = ({
  id,
  sarpid,
  lat,
  lon,
  source,
  hasnetwork,
  stream,
  basin,
  road,
  roadtype,
  crossingtype,
  condition,
  tespp,
  ownertype,
  severityclass,
  // metrics
  upstreammiles,
  downstreammiles,
  sinuosityclass,
  landcover,
  sizeclasses,
}) => {
  const isCrossing = isEmptyString(crossingtype)

  return (
    <div>
      <Section>
        <SectionHeader>Location</SectionHeader>
        <List>
          <li>
            Coordinates: {formatNumber(lat, 3)}
            &deg; N, {formatNumber(lon, 3)}
            &deg; E
          </li>
          {!isEmptyString(stream) ? (
            <li>
              Stream or river: {stream}
              {!isEmptyString(basin) ? `, ${basin} Basin` : null}
            </li>
          ) : null}
          {!isEmptyString(road) ? <li>Road: {road}</li> : null}
          {ownertype && ownertype > 0 && (
            <li>Conservation land type: {OWNERTYPE[ownertype]}</li>
          )}
        </List>
      </Section>

      <SectionHeader>Barrier information</SectionHeader>
      <List>
        <li>
          Barrier type:{' '}
          {isCrossing
            ? 'road / stream crossing'
            : 'road-related potential barrier'}
        </li>
        {!isEmptyString(roadtype) ? <li>Road type: {roadtype}</li> : null}
        {!isEmptyString(crossingtype) ? (
          <li>Crossing type: {crossingtype}</li>
        ) : null}
        {!isEmptyString(condition) ? <li>Condition: {condition}</li> : null}
        {severityclass !== null ? (
          <li>Severity: {BARRIER_SEVERITY[severityclass]}</li>
        ) : null}
      </List>

      <SectionHeader>Functional network information</SectionHeader>
      <List>
        {hasnetwork ? (
          <React.Fragment>
            <li>
              <b>{formatNumber(Math.min(upstreammiles, downstreammiles))}</b>{' '}
              miles could be gained by removing this barrier
              <List>
                <li>
                  {formatNumber(upstreammiles)} miles in the upstream network
                </li>
                <li>
                  {formatNumber(downstreammiles)} miles in the downstream
                  network
                </li>
              </List>
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
          </React.Fragment>
        ) : (
          <li className="has-text-grey">
            {isCrossing
              ? 'This crossing has not yet been evaluated for aquatic connectivity.'
              : 'No functional network information available.  This barrier is off-network or is not a barrier.'}
          </li>
        )}
      </List>

      <SectionHeader>Species information</SectionHeader>
      <List>
        {tespp === null ? (
          <li className="has-text-grey">
            This barrier does not have subwatershed threatened and endangered
            aquatic species information.
          </li>
        ) : (
          <React.Fragment>
            {tespp > 0 ? (
              <React.Fragment>
                <li>
                  <b>{tespp}</b> threatened and endangered aquatic species have
                  been found in the subwatershed containing this barrier.
                </li>
                <li className="has-text-grey is-size-7">
                  Note: species information is very incomplete. These species
                  may or may not be directly impacted by this barrier.
                </li>
              </React.Fragment>
            ) : (
              <li className="has-text-grey">
                No threatened and endangered aquatic species have been
                identified by available data sources for this subwatershed.
              </li>
            )}
          </React.Fragment>
        )}
      </List>

      {!isEmptyString(source) || !isCrossing ? (
        <React.Fragment>
          <SectionHeader>Other information</SectionHeader>
          <List>
            {!isCrossing ? (
              <li>
                SARP ID: {sarpid} (data version: {dataVersion})
              </li>
            ) : null}

            {!isEmptyString(source) ? <li>Source: {source}</li> : null}
          </List>
        </React.Fragment>
      ) : null}
    </div>
  )
}
BarrierDetails.propTypes = {
  id: PropTypes.number.isRequired,
  sarpid: PropTypes.string.isRequired,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  hasnetwork: PropTypes.bool.isRequired,
  source: PropTypes.string,
  stream: PropTypes.string,
  basin: PropTypes.string,
  road: PropTypes.string,
  roadtype: PropTypes.string,
  crossingtype: PropTypes.string,
  condition: PropTypes.string,
  severityclass: PropTypes.number,
  tespp: PropTypes.number,
  ownertype: PropTypes.number,
  upstreammiles: PropTypes.number,
  downstreammiles: PropTypes.number,
  sinuosityclass: PropTypes.number,
  landcover: PropTypes.number,
  sizeclasses: PropTypes.number,
}

BarrierDetails.defaultProps = {
  source: null,
  stream: null,
  basin: null,
  road: null,
  roadtype: null,
  crossingtype: null,
  severityclass: null,
  condition: null,
  tespp: null,
  ownertype: null,
  upstreammiles: null,
  downstreammiles: null,
  sinuosityclass: null,
  landcover: null,
  sizeclasses: null,
}

export default BarrierDetails
