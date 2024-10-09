import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Grid, Heading, Image, Text } from 'theme-ui'

import { siteMetadata, attachmentKeywords } from 'config'
import { OutboundLink } from 'components/Link'
import { isEmptyString } from 'util/string'
import { Entry } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({
  barrierType,
  sarpid,
  nidfederalid,
  nidid,
  source,
  sourceid,
  partnerid,
  sourcelink,
  nearestusgscrossingid,
  attachments: rawAttachments,
  sx,
}) => {
  const fromWDFW = source && source.startsWith('WDFW')
  const fromODFW = source && source.startsWith('ODFW')

  let NIDSection = null

  if (!isEmptyString(nidfederalid) || !isEmptyString(nidid)) {
    // if both are present and equal, only show the latest one
    if (nidfederalid === nidid || (nidfederalid && isEmptyString(nidid))) {
      NIDSection = (
        <Entry>
          National inventory of dams ID:{' '}
          <OutboundLink
            to={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
          >
            {nidfederalid}
          </OutboundLink>
        </Entry>
      )
    } else if (!isEmptyString(nidfederalid) && !isEmptyString(nidid)) {
      // if both are present and not equal, show each
      NIDSection = (
        <Entry>
          National inventory of dams ID:{' '}
          <OutboundLink
            to={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
          >
            {nidfederalid}
          </OutboundLink>
          <br />
          legacy ID: {nidid}
        </Entry>
      )
    } else {
      NIDSection = (
        <Entry>National inventory of dams ID: {nidid} (legacy ID)</Entry>
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
    <Box sx={sx}>
      <Heading as="h3">Data sources</Heading>
      <Box sx={{ mt: '0.5rem' }}>
        <Entry>
          SARP ID: {sarpid} (data version: {dataVersion})
        </Entry>
        {NIDSection}

        {!isEmptyString(source) ? (
          <Entry>
            Source:{' '}
            {source.startsWith('OpenStreetMap') ? (
              <OutboundLink to="https://www.openstreetmap.org/copyright">
                OpenStreetMap
              </OutboundLink>
            ) : (
              source
            )}
          </Entry>
        ) : null}
        {!isEmptyString(sourceid) ? <Entry>Source ID: {sourceid}</Entry> : null}
        {!isEmptyString(sourcelink) ? (
          <Entry>
            More information:{' '}
            <OutboundLink to={sourcelink}>{sourcelink}</OutboundLink>
          </Entry>
        ) : null}

        {!isEmptyString(nearestusgscrossingid) ? (
          <Entry>
            USGS Database of Stream Crossings ID: {nearestusgscrossingid}
            <Text sx={{ fontSize: 0, color: 'grey.7', mt: '0.5rem' }}>
              Note: this crossing is close to the location of this barrier, but
              it may not represent exactly the same barrier that was inventoried
              due to methods used to snap barriers and crossings to the aquatic
              network.
            </Text>
          </Entry>
        ) : null}

        {!isEmptyString(partnerid) ? (
          <Entry>Local Partner ID: {partnerid}</Entry>
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

      {barrierType === 'small_barriers' && attachments.length > 0 ? (
        <Box sx={{ mt: '2rem', ml: '0.5rem' }}>
          <Flex sx={{ gap: '0.5rem', alignItems: 'baseline' }}>
            <Text sx={{ fontWeight: 'bold' }}>Barrier survey photos:</Text>
            <Text sx={{ fontSize: 0 }}>(click for full size)</Text>
          </Flex>
          <Grid columns={Math.min(3, attachments.length)} gap={2}>
            {attachments.map(({ keyword, url }) => (
              <Box key={keyword}>
                <OutboundLink to={url}>
                  <Box
                    sx={{
                      minWidth: '200px',
                    }}
                  >
                    <Flex
                      sx={{
                        overflow: 'hidden',
                        alignItems: 'center',
                      }}
                    >
                      <Image
                        src={url}
                        sx={{
                          width: '100%',
                          border: '1px solid',
                          borderColor: 'grey.7',
                          '&:hover': {
                            borderColor: 'link',
                          },
                        }}
                      />
                    </Flex>
                    <Text
                      sx={{ fontSize: 0, color: 'grey.7', textAlign: 'center' }}
                    >
                      {keyword}
                    </Text>
                  </Box>
                </OutboundLink>
              </Box>
            ))}
          </Grid>
        </Box>
      ) : null}
    </Box>
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
  sourcelink: PropTypes.string,
  nearestusgscrossingid: PropTypes.string,
  attachments: PropTypes.string,
  sx: PropTypes.object,
}

IDInfo.defaultProps = {
  nidfederalid: null,
  nidid: null,
  source: null,
  sourceid: null,
  partnerid: null,
  sourcelink: null,
  nearestusgscrossingid: null,
  attachments: null,
  sx: null,
}

export default IDInfo
