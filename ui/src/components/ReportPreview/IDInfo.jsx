import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { isEmptyString } from 'util/string'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const IDInfo = ({ sarpid, nidid, source }) => (
  <Box>
    <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>Data sources</Text>
    <Box as="ul" sx={{ mt: '0.5rem' }}>
      <li>
        SARP ID: {sarpid} (data version: {dataVersion})
      </li>
      {!isEmptyString(nidid) ? (
        <li>National inventory of dams ID: {nidid}</li>
      ) : null}
      {!isEmptyString(source) ? <li>Source: {source}</li> : null}
    </Box>
  </Box>
)

IDInfo.propTypes = {
  sarpid: PropTypes.string.isRequired,
  nidid: PropTypes.string,
  source: PropTypes.string,
}

IDInfo.defaultProps = {
  nidid: null,
  source: null,
}

export default IDInfo
