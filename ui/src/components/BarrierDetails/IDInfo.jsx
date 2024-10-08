import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Grid, Text, Image } from 'theme-ui'

import { attachmentKeywords } from 'config'
import { ExternalLink, OutboundLink } from 'components/Link'
import { Entry, Field } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

const IDInfo = ({
  barrierType,
  sarpid,
  nidfederalid,
  nidid,
  source,
  sourceid,
  partnerid,
  nearestusgscrossingid,
  sourcelink,
  lat,
  lon,
  attachments: rawAttachments,
}) => {
  const fromWDFW = source && source.startsWith('WDFW')
  const fromODFW = source && source.startsWith('ODFW')

  let NIDSection = null
  if (!isEmptyString(nidfederalid) || !isEmptyString(nidid)) {
    // if both are present and equal, only show the latest one
    if (
      nidfederalid === nidid ||
      (!isEmptyString(nidfederalid) && isEmptyString(nidid))
    ) {
      NIDSection = (
        <Entry>
          <Field label="National inventory of dams ID">
            <ExternalLink
              to={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
            >
              {nidfederalid}
            </ExternalLink>
          </Field>
        </Entry>
      )
    } else if (!isEmptyString(nidfederalid) && !isEmptyString(nidid)) {
      // if both are present and not equal, show each
      NIDSection = (
        <Entry>
          <Field label="National inventory of dams ID">
            <Flex
              sx={{
                flexDirection: 'column',
                alignItems: 'flex-end',
              }}
            >
              <ExternalLink
                to={`https://nid.sec.usace.army.mil/#/dams/system/${nidfederalid}/summary`}
              >
                {nidfederalid}
              </ExternalLink>
              <Text sx={{ fontSize: 0 }}>legacy ID: {nidid}</Text>
            </Flex>
          </Field>
        </Entry>
      )
    } else {
      // only NIDID is available, link to that
      NIDSection = (
        <Entry>
          <Field label="National inventory of dams ID">
            <ExternalLink to="https://nid.sec.usace.army.mil/#/">
              {nidid}
            </ExternalLink>{' '}
            <Text sx={{ fontSize: 0 }}>(legacy ID)</Text>
          </Field>
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
    <>
      {!isEmptyString(sarpid) ? (
        <Entry>
          <Field label="SARP ID">{sarpid}</Field>
        </Entry>
      ) : null}

      {NIDSection}

      {!isEmptyString(source) ? (
        <Entry>
          <Field label="Source">
            <Text sx={{ textAlign: 'right' }}>
              {source.startsWith('OpenStreetMap') ? (
                <OutboundLink to="https://www.openstreetmap.org/copyright">
                  OpenStreetMap
                </OutboundLink>
              ) : (
                source
              )}
            </Text>
          </Field>
        </Entry>
      ) : null}

      {!isEmptyString(sourceid) ? (
        <Entry>
          <Field label="Source ID">
            <Text sx={{ textAlign: 'right' }}>{sourceid}</Text>
          </Field>
        </Entry>
      ) : null}

      {!isEmptyString(sourcelink) ? (
        <Entry>
          <ExternalLink to={sourcelink}>
            Click here for more information about this barrier
          </ExternalLink>
        </Entry>
      ) : null}

      {fromWDFW ? (
        <Entry>
          Information about this barrier is maintained by the{' '}
          <OutboundLink to="https://wdfw.wa.gov/species-habitats/habitat-recovery/fish-passage">
            Washington State Department of Fish and Wildlife, Fish Passage
            Division
          </OutboundLink>
          . For more information about specific structures, please visit the{' '}
          <OutboundLink to="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html">
            fish passage web map
          </OutboundLink>
          .
        </Entry>
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

      {!isEmptyString(partnerid) ? (
        <Entry>
          <Field label="Local Partner ID">{partnerid}</Field>
        </Entry>
      ) : null}

      {!isEmptyString(nearestusgscrossingid) ? (
        <Entry>
          <Field label="USGS Database of Stream Crossings ID">
            {nearestusgscrossingid}
          </Field>
          <Text sx={{ fontSize: 0, color: 'grey.7', mt: '0.5rem' }}>
            Note: this crossing is close to the location of this barrier, but it
            may not represent exactly the same barrier that was inventoried due
            to methods used to snap barriers and crossings to the aquatic
            network.
          </Text>
        </Entry>
      ) : null}

      <Entry>
        <Field label="View location in Google Maps">
          <Flex sx={{ flex: '0 0 auto', gap: '0.5rem' }}>
            <Box sx={{ flex: '0 0 auto' }}>
              <ExternalLink
                to={`https://www.google.com/maps/search/?api=1&query=${lat},${lon}`}
              >
                map
              </ExternalLink>
            </Box>
            {barrierType === 'small_barriers' ||
            barrierType === 'road_crossings' ? (
              <Box
                sx={{
                  flex: '0 0 auto',
                  borderLeft: '1px solid',
                  borderLeftColor: 'grey.3',
                  pl: '0.5rem',
                }}
              >
                <ExternalLink
                  to={`https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}&fov=100`}
                >
                  street view
                </ExternalLink>
              </Box>
            ) : null}
          </Flex>
        </Field>
      </Entry>

      {barrierType === 'small_barriers' && attachments.length > 0 ? (
        <Entry>
          <Text>Barrier survey photos:</Text>
          <Grid columns={Math.min(2, attachments.length)} gap={2}>
            {attachments.map(({ keyword, url }) => (
              <Box key={keyword}>
                <OutboundLink to={url}>
                  <Box
                    sx={{
                      maxWidth: '200px',
                      minWidth: '100px',
                    }}
                  >
                    <Flex
                      sx={{
                        overflow: 'hidden',
                        maxHeight: '110px',
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
        </Entry>
      ) : null}
    </>
  )
}

IDInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string,
  nidfederalid: PropTypes.string,
  nidid: PropTypes.string,
  source: PropTypes.string,
  sourceid: PropTypes.string,
  partnerid: PropTypes.string,
  nearestusgscrossingid: PropTypes.string,
  sourcelink: PropTypes.string,
  lat: PropTypes.number.isRequired,
  lon: PropTypes.number.isRequired,
  attachments: PropTypes.string,
}

IDInfo.defaultProps = {
  sarpid: null,
  nidfederalid: null,
  nidid: null,
  source: null,
  sourceid: null,
  partnerid: null,
  nearestusgscrossingid: null,
  sourcelink: null,
  attachments: null,
}

export default IDInfo
