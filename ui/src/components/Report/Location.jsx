import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import { List, ListItem } from './elements'

import { OWNERTYPE } from '../../../config/constants'

const Location = ({ river, HUC12Name, HUC12, HUC8Name, HUC8, ownertype }) => {
  const hasRiver =
    river && river !== '"' && river !== 'null' && river !== 'Unknown'

  const hasOwner = ownertype && ownertype > 0

  if (!(hasRiver || HUC12 || hasOwner)) {
    return null
  }

  return (
    <List title="Location information">
      {hasRiver ? (
        <ListItem>
          <Text>River or stream: {river}</Text>
        </ListItem>
      ) : null}

      {HUC12 ? (
        <>
          <ListItem>
            <Text>
              Subwatershed: {HUC12Name} (HUC12: {HUC12})
            </Text>
          </ListItem>
          <ListItem>
            <Text>
              Subbasin: {HUC8Name} (HUC8: {HUC8})
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
  HUC12: PropTypes.string,
  HUC8: PropTypes.string,
  HUC12Name: PropTypes.string,
  HUC8Name: PropTypes.string,
  ownertype: PropTypes.number,
}

Location.defaultProps = {
  river: null,
  HUC12: null,
  HUC8: null,
  HUC12Name: null,
  HUC8Name: null,
  ownertype: null,
}

export default Location
