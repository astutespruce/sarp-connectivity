import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Grid } from 'theme-ui'

import { formatNumber, pluralize } from 'util/format'

const DiadromousInfo = ({
  barrierType,
  milestooutlet,
  totaldownstreamdams,
  totaldownstreamsmallbarriers,
  totaldownstreamwaterfalls,
  sx,
}) => {
  const numCols =
    1 +
    (totaldownstreamdams >= 0) +
    (barrierType === 'small_barriers' && totaldownstreamsmallbarriers >= 0) +
    (totaldownstreamwaterfalls >= 0)

  return (
    <Box sx={sx}>
      <Heading as="h3">Diadromous species information</Heading>
      <Grid
        columns={numCols}
        gap={0}
        sx={{
          mt: '1rem',
          '&>div': {
            py: '0.5em',
          },
          '&> div + div': {
            ml: '1rem',
            pl: '1rem',
            borderLeft: '1px solid',
            borderLeftColor: 'grey.3',
          },
        }}
      >
        <Box>
          <b>{formatNumber(milestooutlet)}</b>{' '}
          {pluralize('mile', milestooutlet)} downstream to the ocean
        </Box>
        {totaldownstreamdams >= 0 ? (
          <Box>
            <b>{formatNumber(totaldownstreamdams)}</b>{' '}
            {pluralize('dam', totaldownstreamdams)} downstream
          </Box>
        ) : null}
        {barrierType === 'small_barriers' &&
        totaldownstreamsmallbarriers >= 0 ? (
          <Box>
            <b>{formatNumber(totaldownstreamsmallbarriers)}</b> assessed
            road-related {pluralize('barrier', totaldownstreamsmallbarriers)}{' '}
            downstream
          </Box>
        ) : null}
        {totaldownstreamwaterfalls >= 0 ? (
          <Box>
            <b>{formatNumber(totaldownstreamwaterfalls)}</b>{' '}
            {pluralize('waterfall', totaldownstreamwaterfalls)} downstream
          </Box>
        ) : null}
      </Grid>
    </Box>
  )
}

DiadromousInfo.propTypes = {
  barrierType: PropTypes.string.isRequired,
  milestooutlet: PropTypes.number,
  totaldownstreamdams: PropTypes.number,
  totaldownstreamsmallbarriers: PropTypes.number,
  totaldownstreamwaterfalls: PropTypes.number,
  sx: PropTypes.object,
}

DiadromousInfo.defaultProps = {
  milestooutlet: 0,
  totaldownstreamdams: 0,
  totaldownstreamsmallbarriers: 0,
  totaldownstreamwaterfalls: 0,
  sx: null,
}

export default DiadromousInfo
