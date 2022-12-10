import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { siteMetadata } from 'config'
import { isEmptyString } from 'util/string'

import { Link, Entry, Entries, Section } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({ sarpid, nidid, source, link, ...props }) => (
  <Section title="Data sources" {...props} wrap={false}>
    <Entries>
      <Entry>
        <Text>
          SARP ID: {sarpid} (data version: {dataVersion})
        </Text>
      </Entry>
      {!isEmptyString(nidid) ? (
        <Entry>
          <Text>National inventory of dams ID: {nidid}</Text>
        </Entry>
      ) : null}
      {!isEmptyString(source) ? (
        <Entry>
          <Text>Source: {source}</Text>
        </Entry>
      ) : null}
      {!isEmptyString(link) ? (
        <Entry>
          <Text>More information:</Text>
          <Link href={link}>
            <Text>{link}</Text>
          </Link>
        </Entry>
      ) : null}
    </Entries>

    {source && source.startsWith('WDFW') ? (
      <Text style={{ marginTop: 24 }}>
        Information about this barrier is maintained by the Washington State
        Department of Fish and Wildlife, Fish Passage Division. For more
        information about specific structures, please visit the{' '}
        <Link href="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html">
          <Text>fish passage web map</Text>
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
