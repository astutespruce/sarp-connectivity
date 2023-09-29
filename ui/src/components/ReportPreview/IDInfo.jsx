import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text } from 'theme-ui'

import { siteMetadata } from 'config'
import { OutboundLink } from 'components/Link'
import { isEmptyString } from 'util/string'
import { Entry } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({ sarpid, nidid, source, link, nearestcrossingid, sx }) => {
  const fromWDFW = source && source.startsWith('WDFW')
  const fromODFW = source && source.startsWith('ODFW')

  return (
    <Box sx={sx}>
      <Heading as="h3">Data sources</Heading>
      <Box sx={{ mt: '0.5rem' }}>
        <Entry>
          SARP ID: {sarpid} (data version: {dataVersion})
        </Entry>
        {!isEmptyString(nidid) ? (
          <Entry>National inventory of dams ID: {nidid}</Entry>
        ) : null}
        {!isEmptyString(source) ? <Entry>Source: {source}</Entry> : null}
        {!isEmptyString(link) ? (
          <Entry>
            More information: <OutboundLink to={link}>{link}</OutboundLink>
          </Entry>
        ) : null}

        {!isEmptyString(nearestcrossingid) ? (
          <Entry>
            USGS Database of Stream Crossings ID:{' '}
            {nearestcrossingid.replace('cr', '')}
            <Text sx={{ fontSize: 0, color: 'grey.7', mt: '0.5rem' }}>
              Note: this crossing is close to the location of this barrier, but
              it may not represent exactly the same barrier that was inventoried
              due to methods used to snap barriers and crossings to the aquatic
              network.
            </Text>
          </Entry>
        ) : null}
      </Box>

      {fromWDFW ? (
        <Box sx={{ mt: '2rem' }}>
          Information about this barrier is maintained by the Washington State
          Department of Fish and Wildlife, Fish Passage Division. For more
          information about specific structures, please visit the{' '}
          <OutboundLink to="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html">
            fish passage web map
          </OutboundLink>
          .
        </Box>
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
    </Box>
  )
}

IDInfo.propTypes = {
  sarpid: PropTypes.string.isRequired,
  nidid: PropTypes.string,
  source: PropTypes.string,
  link: PropTypes.string,
  nearestcrossingid: PropTypes.string,
  sx: PropTypes.object,
}

IDInfo.defaultProps = {
  nidid: null,
  source: null,
  link: null,
  nearestcrossingid: null,
  sx: null,
}

export default IDInfo
