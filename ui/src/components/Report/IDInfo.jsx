import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { isEmptyString } from 'util/string'

import { List, ListItem } from './elements'
import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const IDInfo = ({ sarpid, nidid, source }) => (
  <List title="Data sources">
    <ListItem>
      <Text>
        SARP ID: {sarpid} (data version: {dataVersion})
      </Text>
    </ListItem>
    {!isEmptyString(nidid) ? (
      <ListItem>
        <Text>National inventory of dams ID: {nidid}</Text>
      </ListItem>
    ) : null}
    {!isEmptyString(source) ? (
      <ListItem>
        <Text>Source: {source}</Text>
      </ListItem>
    ) : null}
  </List>
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
