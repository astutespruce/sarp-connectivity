import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { List, ListItem } from './elements'

import { OWNERTYPE } from '../../../config/constants'

const Location = ({
  river,
  subwatershed,
  subbasin,
  huc12,
  huc8,
  ownertype,
}) => {
  const hasRiver =
    river && river !== '"' && river !== 'null' && river !== 'Unknown'

  const hasOwner = ownertype && ownertype > 0

  if (!(hasRiver || huc12 || hasOwner)) {
    return null
  }

  return (
    <List title="Location information">
      {hasRiver ? (
        <ListItem>
          <Text>River or stream: {river}</Text>
        </ListItem>
      ) : null}

      {huc12 ? (
        <>
          <ListItem>
            <Text>
              Subwatershed: {subwatershed} {'\n'} (HUC12: {huc12})
            </Text>
          </ListItem>
          <ListItem>
            <Text>
              Subbasin: {subbasin} {'\n'} (HUC8: {huc8})
            </Text>
          </ListItem>
        </>
      ) : null}
      {hasOwner ? (
        <ListItem>
          <Text>Conservation land type: {OWNERTYPE[ownertype]}</Text>
        </ListItem>
      ) : null}
    </List>
  )
}

Location.propTypes = {
  river: PropTypes.string,
  huc12: PropTypes.string,
  huc8: PropTypes.string,
  subwatershed: PropTypes.string,
  subbasin: PropTypes.string,
  ownertype: PropTypes.number,
}

Location.defaultProps = {
  river: null,
  huc12: null,
  huc8: null,
  subwatershed: null,
  subbasin: null,
  ownertype: null,
}

export default Location
