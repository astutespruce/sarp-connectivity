import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { siteMetadata } from 'config'
import { isEmptyString } from 'util/string'

import { Link, Entry, Entries, Section } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({
  sarpid,
  nidid,
  source,
  sourceid,
  partnerid,
  link,
  nearestcrossingid,
  ...props
}) => {
  const fromWDFW = source && source.startsWith('WDFW')
  const fromODFW = source && source.startsWith('ODFW')

  return (
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

        {!isEmptyString(sourceid) ? (
          <Entry>
            <Text>Source ID: {sourceid}</Text>
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

        {!isEmptyString(nearestcrossingid) ? (
          <Entry>
            <Text>
              USGS Database of Stream Crossings ID:{' '}
              {nearestcrossingid.replace('cr', '')}
            </Text>
            <Text style={{ color: '#7f8a93', marginTop: 6, fontSize: 10 }}>
              Note: this crossing is close to the location of this barrier, but
              it may not represent exactly the same barrier that was inventoried
              due to methods used to snap barriers and crossings to the aquatic
              network.
            </Text>
          </Entry>
        ) : null}

        {!isEmptyString(partnerid) ? (
          <Entry>
            <Text>Local Partner ID: {partnerid}</Text>
          </Entry>
        ) : null}
      </Entries>

      {fromWDFW ? (
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

      {fromODFW ? (
        <Entry>
          Information about this barrier is maintained by the{' '}
          <Link href="https://www.dfw.state.or.us/fish/passage/inventories.asp">
            Oregon Department of Fish and Wildlife
          </Link>
          .
        </Entry>
      ) : null}
    </Section>
  )
}

IDInfo.propTypes = {
  sarpid: PropTypes.string.isRequired,
  nidid: PropTypes.string,
  source: PropTypes.string,
  sourceid: PropTypes.string,
  partnerid: PropTypes.string,
  link: PropTypes.string,
  nearestcrossingid: PropTypes.string,
}

IDInfo.defaultProps = {
  nidid: null,
  source: null,
  sourceid: null,
  partnerid: null,
  link: null,
  nearestcrossingid: null,
}

export default IDInfo
