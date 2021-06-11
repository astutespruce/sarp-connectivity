import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { OWNERTYPE } from '../../../config/constants'

const Location = ({
  river,
  subbasin,
  subwatershed,
  huc8,
  huc12,
  ownertype,
}) => {
  const hasRiver =
    river && river !== '"' && river !== 'null' && river !== 'Unknown'

  const hasOwner = ownertype && ownertype > 0

  if (!(hasRiver || huc12 || hasOwner)) {
    return null
  }

  return (
    <Box>
      <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
        Location information:
      </Text>

      <Box as="ul" sx={{ mt: '0.5rem' }}>
        {hasRiver ? <li>River or stream: {river}</li> : null}

        {huc12 ? (
          <>
            <li>
              Subwatershed: {subwatershed} (HUC12: {huc12})
            </li>
            <li>
              Subbasin: {subbasin} (HUC8: {huc8})
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
