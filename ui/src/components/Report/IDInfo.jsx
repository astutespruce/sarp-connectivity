import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { siteMetadata } from 'config'
import { isEmptyString } from 'util/string'

import { Link, List, ListItem, Section } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({ sarpid, nidid, source, link, ...props }) => (
  <Section title="Data sources" {...props} wrap={false}>
    <List>
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
      {!isEmptyString(link) ? (
        <ListItem>
          <Text>
            More information: <Link href={link}>{link}</Link>
          </Text>
        </ListItem>
      ) : null}
    </List>

    {source && source.startsWith('WDFW') ? (
      <Text style={{ marginTop: 24 }}>
        Information about this barrier is maintained by the Washington State
        Department of Fish and Wildlife, Fish Passage Division. For more
        information about specific structures, please visit the{' '}
        <Link href="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html">
          fish passage web map
        </Link>
        .
      </Text>
    ) : null}
  </Section>
)

IDInfo.propTypes = {
  sarpid: PropTypes.string.isRequired,
  nidid: PropTypes.string,
  source: PropTypes.string,
  link: PropTypes.string,
}

IDInfo.defaultProps = {
  nidid: null,
  source: null,
  link: null,
}

export default IDInfo
