import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading } from 'theme-ui'

import { siteMetadata } from 'config'
import { OutboundLink } from 'components/Link'
import { isEmptyString } from 'util/string'
import { Entry } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({ sarpid, nidid, source, link, sx }) => (
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
    </Box>

    {source && source.startsWith('WDFW') ? (
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
  </Box>
)

IDInfo.propTypes = {
  sarpid: PropTypes.string.isRequired,
  nidid: PropTypes.string,
  source: PropTypes.string,
  link: PropTypes.string,
  sx: PropTypes.object,
}

IDInfo.defaultProps = {
  nidid: null,
  source: null,
  link: null,
  sx: null,
}

export default IDInfo
