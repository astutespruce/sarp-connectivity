import React from 'react'
import PropTypes from 'prop-types'
import { Image, Text, View } from '@react-pdf/renderer'

import { siteMetadata, attachmentKeywords } from 'config'
import { isEmptyString } from 'util/string'

import { Bold, Flex, Link, Entry, Entries, Section } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({
  barrierType,
  sarpid,
  nidfederalid,
  nidid,
  source,
  sourceid,
  partnerid,
  link,
  nearestusgscrossingid,
  attachments: rawAttachments,
  ...props
}) => {
  const fromWDFW = source && source.startsWith('WDFW')
  const fromODFW = source && source.startsWith('ODFW')

  let NIDSection = null
  if (!isEmptyString(nidfederalid) || !isEmptyString(nidid)) {
    // if both are present and equal, only show the latest one
    if (nidfederalid === nidid || (nidfederalid && isEmptyString(nidid))) {
      NIDSection = (
        <Entry>
          <Text>
            National inventory of dams ID:
            <Link
              href={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
            >
              <Text>{nidfederalid}</Text>
            </Link>
          </Text>
        </Entry>
      )
    } else if (!isEmptyString(nidfederalid) && !isEmptyString(nidid)) {
      // if both are present and not equal, show each
      NIDSection = (
        <Entry>
          <Text>
            National inventory of dams ID:{' '}
            <Link
              href={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
            >
              <Text>{nidfederalid}</Text>
            </Link>{' '}
            (legacy ID: {nidid})
          </Text>
        </Entry>
      )
    } else {
      NIDSection = (
        <Entry>
          <Text>National inventory of dams ID: {nidid} (legacy ID)</Text>
        </Entry>
      )
    }
  }

  let attachments = []
  if (!isEmptyString(rawAttachments)) {
    const [prefix, parts] = rawAttachments.split('|')
    attachments = parts
      .split(',')
      .sort((a, b) =>
        attachmentKeywords.indexOf(a.split(':')[0]) <
        attachmentKeywords.indexOf(b.split(':')[0])
          ? -1
          : 1
      )
      .map((part) => {
        const [keyword, partId] = part.split(':')
        return { keyword, url: `${prefix}/${partId}` }
      })
  }

  return (
    <Section title="Data sources" {...props} wrap>
      <Entries>
        <Entry>
          <Text>
            SARP ID: {sarpid} (data version: {dataVersion})
          </Text>
        </Entry>

        {NIDSection}

        {!isEmptyString(source) ? (
          <Entry>
            <Text>
              Source:{' '}
              {source.startsWith('OpenStreetMap') ? (
                <Link href="https://www.openstreetmap.org/copyright">
                  OpenStreetMap
                </Link>
              ) : (
                source
              )}
            </Text>
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

        {!isEmptyString(nearestusgscrossingid) ? (
          <Entry>
            <Text>
              USGS Database of Stream Crossings ID: {nearestusgscrossingid}
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
          <Text>
            Information about this barrier is maintained by the{' '}
            <Link href="https://www.dfw.state.or.us/fish/passage/inventories.asp">
              Oregon Department of Fish and Wildlife
            </Link>
            .
          </Text>
        </Entry>
      ) : null}

      {barrierType === 'small_barriers' && attachments.length > 0 ? (
        <View style={{ marginTop: 14, marginLeft: 6 }}>
          <Flex style={{ alignItems: 'baseline' }}>
            <Text>
              <Bold>Barrier survey photos:</Bold>{' '}
            </Text>
            <Text style={{ fontSize: 10 }}>(click for full size)</Text>
          </Flex>
          <Flex style={{ gap: '1rem', flexWrap: 'wrap' }}>
            {attachments.map(({ keyword, url }, i) => (
              <View
                key={keyword}
                style={{
                  flex: '0 0 170',
                  marginLeft: i % 3 > 0 ? 6 : 0,
                  marginTop: i >= 3 ? 10 : 0,
                  maxHeight: 240,
                  overflow: 'hidden',
                }}
              >
                <Link href={url}>
                  <Image
                    src={url}
                    style={{
                      width: '100%',
                      border: '1px solid #7f8a93',
                    }}
                  />
                  <Text
                    style={{
                      color: '#7f8a93',
                      fontSize: 10,
                      textAlign: 'center',
                    }}
                  >
                    {keyword}
                  </Text>
                </Link>
              </View>
            ))}
          </Flex>
        </View>
      ) : null}
    </Section>
  )
}

IDInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  nidfederalid: PropTypes.string,
  nidid: PropTypes.string,
  source: PropTypes.string,
  sourceid: PropTypes.string,
  partnerid: PropTypes.string,
  link: PropTypes.string,
  nearestusgscrossingid: PropTypes.string,
  attachments: PropTypes.string,
}

IDInfo.defaultProps = {
  nidfederalid: null,
  nidid: null,
  source: null,
  sourceid: null,
  partnerid: null,
  link: null,
  nearestusgscrossingid: null,
  attachments: null,
}

export default IDInfo
