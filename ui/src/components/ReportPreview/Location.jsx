import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { OWNERTYPE } from '../../../config/constants'

const Location = ({ river, HUC12Name, HUC12, HUC8Name, HUC8, ownertype }) => {
  const hasRiver =
    river && river !== '"' && river !== 'null' && river !== 'Unknown'

  const hasOwner = ownertype && ownertype > 0

  if (!(hasRiver || HUC12 || hasOwner)) {
    return null
  }

  return (
    <Box>
      <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
        Location information:
      </Text>

      <Box as="ul" sx={{ mt: '0.5rem' }}>
        {hasRiver ? <li>River or stream: {river}</li> : null}

        {HUC12 ? (
          <>
            <li>
              Subwatershed: {HUC12Name} (HUC12: {HUC12})
            </li>
            <li>
              Subbasin: {HUC8Name} (HUC8: {HUC8})
            </li>
          </>
        ) : null}
        {hasOwner ? (
          <li>Conservation land type: {OWNERTYPE[ownertype]}</li>
        ) : null}
      </Box>
    </Box>
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
