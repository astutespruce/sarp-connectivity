import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Grid, Paragraph } from 'theme-ui'

import { formatNumber } from 'util/format'

const Species = ({
  barrierType,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  ...props
}) => (
  <Box {...props}>
    <Heading as="h3">Species information</Heading>

    <Box>
      Data sources in the subwatershed containing this{' '}
      {barrierType === 'dams' ? 'dam' : 'road-related barrier'} have recorded:
    </Box>

    <Grid
      columns={4}
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
        <b>{formatNumber(tespp)}</b> federally-listed threatened and endangered
        aquatic species
      </Box>
      <Box>
        <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
        Conservation Need (SGCN)
      </Box>
      <Box>
        <b>{regionalsgcnspp}</b> regionally-listed aquatic Species of Greatest
        Conservation Need
      </Box>
      <Box>{trout ? 'One or more trout species' : 'No trout species'}</Box>
    </Grid>

    <Paragraph variant="help" sx={{ mt: '2rem', fontSize: 0 }}>
      Note: State and regionally listed species of greatest conservation need
      may include state-listed threatened and endangered species. Species
      information is very incomplete and only includes species that have been
      identified by available data sources for this subwatershed. These species
      may or may not be directly impacted by this barrier. The absence of
      species in the available data does not necessarily indicate the absence of
      species in the subwatershed.
    </Paragraph>
  </Box>
)

Species.propTypes = {
  barrierType: PropTypes.string.isRequired,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
}

Species.defaultProps = {
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: false,
}

export default Species
