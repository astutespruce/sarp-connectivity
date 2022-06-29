/* eslint-disable camelcase */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { formatNumber } from 'util/format'

const Dams = ({ dams, rankedDams }) => {
  const unrankedDams = dams - rankedDams

  if (dams === 0) {
    return (
      <Paragraph variant="help">
        This area does not yet have any inventoried dams
      </Paragraph>
    )
  }

  return (
    <>
      <Paragraph>This area contains:</Paragraph>

      <Box as="ul" sx={{ mt: '1rem' }}>
        <li>
          <b>{formatNumber(dams, 0)}</b> inventoried{' '}
          {dams === 1 ? 'dam' : 'dams'}
        </li>
        <li>
          <b>{formatNumber(rankedDams, 0)}</b>{' '}
          {rankedDams === 1 ? 'dam' : 'dams'} that{' '}
          {rankedDams === 1 ? 'was ' : 'were '} analyzed for impacts to aquatic
          connectivity in this tool
        </li>
      </Box>
      <Paragraph variant="help" sx={{ mt: '2rem' }}>
        Note: These statistics are based on <i>inventoried</i> dams. Because the
        inventory is incomplete in many areas, areas with a high number of dams
        may simply represent areas that have a more complete inventory.
        {unrankedDams > 0 ? (
          <>
            <br />
            <br />
            {formatNumber(unrankedDams, 0)}{' '}
            {unrankedDams === 1 ? 'dam' : 'dams'} were not analyzed because they
            were not on the aquatic network or could not be correctly located on
            the network.
          </>
        ) : null}
      </Paragraph>
    </>
  )
}

Dams.propTypes = {
  dams: PropTypes.number,
  rankedDams: PropTypes.number,
}

Dams.defaultProps = {
  dams: 0,
  rankedDams: 0,
}

export default Dams
