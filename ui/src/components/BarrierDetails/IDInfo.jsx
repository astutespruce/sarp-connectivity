import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { ExternalLink, OutboundLink } from 'components/Link'
import { Entry, Field } from 'components/Sidebar'
import { isEmptyString } from 'util/string'

const IDInfo = ({ sarpid, nidid, source, link }) => (
  <>
    {!isEmptyString(sarpid) ? (
      <Entry>
        <Field label="SARP ID">{sarpid}</Field>
      </Entry>
    ) : null}
    {!isEmptyString(nidid) ? (
      <Entry>
        <Field label="National inventory of dams ID">
          <ExternalLink to="https://nid.usace.army.mil/#/">
            {nidid}
          </ExternalLink>
        </Field>
      </Entry>
    ) : null}

    {!isEmptyString(source) ? (
      <Entry>
        <Field label="Source">
          <Text sx={{ textAlign: 'right' }}>{source}</Text>
        </Field>
      </Entry>
    ) : null}

    {!isEmptyString(link) ? (
      <Entry>
        <ExternalLink to={link}>
          Click here for more information about this barrier
        </ExternalLink>
      </Entry>
    ) : null}

    {source && source.startsWith('WDFW') ? (
      <Entry>
        Information about this barrier is maintained by the Washington State
        Department of Fish and Wildlife, Fish Passage Division. For more
        information about specific structures, please visit the{' '}
        <OutboundLink to="https://geodataservices.wdfw.wa.gov/hp/fishpassage/index.html">
          fish passage web map
        </OutboundLink>
        .
      </Entry>
    ) : null}
  </>
)

IDInfo.propTypes = {
  sarpid: PropTypes.string,
  nidid: PropTypes.string,
  source: PropTypes.string,
  link: PropTypes.string,
}

IDInfo.defaultProps = {
  sarpid: null,
  nidid: null,
  source: null,
  link: null,
}

export default IDInfo
