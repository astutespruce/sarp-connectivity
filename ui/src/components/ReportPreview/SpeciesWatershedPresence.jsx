import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Grid, Paragraph, Text } from 'theme-ui'

import { SALMONID_ESU } from 'config'
import { formatNumber } from 'util/format'

const SpeciesWatershedPresence = ({
  barrierType,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  sx,
}) => (
  <Box sx={sx}>
    <Heading as="h3">Species information for this subwatershed</Heading>

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

    {salmonidesu ? (
      <Text sx={{ mt: '1.5rem' }}>
        This subwatershed falls within the following salmon Evolutionarily
        Significant Units (ESU) / steelhead trout Discrete Population Segments
        (DPS):
        <Box as="ul" sx={{ mt: '0.25rem', ml: '1rem' }}>
          {salmonidesu.split(',').map((code) => (
            <li key={code}>{SALMONID_ESU[code]}</li>
          ))}
        </Box>
      </Text>
    ) : null}

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

SpeciesWatershedPresence.propTypes = {
  barrierType: PropTypes.string.isRequired,
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
  trout: PropTypes.number,
  salmonidesu: PropTypes.string,
  sx: PropTypes.object,
}

SpeciesWatershedPresence.defaultProps = {
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
  trout: 0,
  salmonidesu: null,
  sx: null,
}

export default SpeciesWatershedPresence
