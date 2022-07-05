import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading } from 'theme-ui'

import { OutboundLink } from 'components/Link'
import { isEmptyString } from 'util/string'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const IDInfo = ({ sarpid, nidid, source, link, sx }) => (
  <Box sx={sx}>
    <Heading as="h3">Data sources</Heading>
    <Box as="ul" sx={{ mt: '0.5rem' }}>
      <li>
        SARP ID: {sarpid} (data version: {dataVersion})
      </li>
      {!isEmptyString(nidid) ? (
        <li>National inventory of dams ID: {nidid}</li>
      ) : null}
      {!isEmptyString(source) ? <li>Source: {source}</li> : null}
      {!isEmptyString(link) ? (
        <li>
          More information: <OutboundLink to={link}>{link}</OutboundLink>
        </li>
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
