import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Text } from 'theme-ui'

import { siteMetadata } from 'config'
import { OutboundLink } from 'components/Link'
import { isEmptyString } from 'util/string'
import { Entry } from './elements'

const { version: dataVersion } = siteMetadata

const IDInfo = ({
  sarpid,
  nidfederalid,
  nidid,
  source,
  sourceid,
  partnerid,
  link,
  nearestusgscrossingid,
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
        {!isEmptyString(link) ? (
          <Entry>
            More information: <OutboundLink to={link}>{link}</OutboundLink>
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
    </Box>
  )
}

IDInfo.propTypes = {
  sarpid: PropTypes.string.isRequired,
  nidfederalid: PropTypes.string,
  nidid: PropTypes.string,
  source: PropTypes.string,
  sourceid: PropTypes.string,
  partnerid: PropTypes.string,
  link: PropTypes.string,
  nearestusgscrossingid: PropTypes.string,
  sx: PropTypes.object,
}

IDInfo.defaultProps = {
  nidfederalid: null,
  nidid: null,
  source: null,
  sourceid: null,
  partnerid: null,
  link: null,
  nearestusgscrossingid: null,
  sx: null,
}

export default IDInfo
