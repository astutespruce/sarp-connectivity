import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { ExternalLink, OutboundLink } from 'components/Link'
import { Entry, Field } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

const IDInfo = ({ sarpid, nidid, source, link, nearestcrossingid }) => {
  const fromWDFW = source && source.startsWith('WDFW')
  const fromODFW = source && source.startsWith('ODFW')

  return (
    <>
      {!isEmptyString(sarpid) ? (
        <Entry>
          <Field label="SARP ID">{sarpid}</Field>
        </Entry>
      ) : null}
      {!isEmptyString(nidid) ? (
        <Entry>
          <Field label="National inventory of dams ID">
            <ExternalLink to="https://nid.usace.army.mil/#/">
              {nidid}
            </ExternalLink>
          </Field>
        </Entry>
      ) : null}

      {!isEmptyString(source) ? (
        <Entry>
          <Field label="Source">
            <Text sx={{ textAlign: 'right' }}>{source}</Text>
          </Field>
        </Entry>
      ) : null}

      {!isEmptyString(link) ? (
        <Entry>
          <ExternalLink to={link}>
            Click here for more information about this barrier
          </ExternalLink>
        </Entry>
      ) : null}

      {fromWDFW ? (
        <Entry>
          Information about this barrier is maintained by the{' '}
          <OutboundLink to="https://wdfw.wa.gov/species-habitats/habitat-recovery/fish-passage">
            Washington State Department of Fish and Wildlife, Fish Passage
            Division
          </OutboundLink>
          . For more information about specific structures, please visit the{' '}
          <OutboundLink to="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html">
            fish passage web map
          </OutboundLink>
          .
        </Entry>
      ) : null}

      {fromODFW ? (
        <Entry>
          Information about this barrier is maintained by the{' '}
          <OutboundLink to="https://www.dfw.state.or.us/fish/passage/inventories.asp">
            Oregon Department of Fish and Wildlife
          </OutboundLink>
          .
        </Entry>
      ) : null}

      {!isEmptyString(nearestcrossingid) ? (
        <Entry>
          <Field label="USGS Database of Stream Crossings ID">
            {nearestcrossingid.replace('cr', '')}
          </Field>
          <Text sx={{ fontSize: 0, color: 'grey.7', mt: '0.5rem' }}>
            Note: this crossing is close to the location of this barrier, but it
            may not represent exactly the same barrier that was inventoried due
            to methods used to snap barriers and crossings to the aquatic
            network.
          </Text>
        </Entry>
      ) : null}
    </>
  )
}

IDInfo.propTypes = {
  sarpid: PropTypes.string,
  nidid: PropTypes.string,
  source: PropTypes.string,
  link: PropTypes.string,
  nearestcrossingid: PropTypes.string,
}

IDInfo.defaultProps = {
  sarpid: null,
  nidid: null,
  source: null,
  link: null,
  nearestcrossingid: null,
}

export default IDInfo
