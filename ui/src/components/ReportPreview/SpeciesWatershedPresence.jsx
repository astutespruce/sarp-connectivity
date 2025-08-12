import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Grid, Paragraph, Text } from 'theme-ui'

import { SALMONID_ESU, TROUT } from 'config'
import {
  SpeciesWatershedPresencePropTypeStub,
  SpeciesWatershedPresenceDefaultProps,
} from 'components/BarrierDetails/proptypes'
import { formatNumber } from 'util/format'

const SpeciesWatershedPresence = ({
  barrierType,
  tespp,
  statesgcnspp,
  regionalsgcnspp,
  trout,
  salmonidesu,
  sx,
}) => {
  const troutSpp = trout ? trout.split(',').map((code) => TROUT[code]) : []

  return (
    <Box sx={sx}>
      <Heading as="h3">Species information for this subwatershed</Heading>

      <Box>
        Data sources in the subwatershed containing this{' '}
        {barrierType === 'dams' ? 'dam' : 'road-related barrier'} have recorded:
      </Box>

      <Grid
        columns={3}
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
          <b>{formatNumber(tespp)}</b> federally-listed threatened and
          endangered aquatic species
        </Box>
        <Box>
          <b>{statesgcnspp}</b> state-listed aquatic Species of Greatest
          Conservation Need (SGCN)
        </Box>
        <Box>
          <b>{regionalsgcnspp}</b> regionally-listed aquatic Species of Greatest
          Conservation Need
        </Box>
      </Grid>

      <Box sx={{ mt: '1.5rem' }}>
        <Text>
          {trout
            ? `This subwatershed includes recorded observations of ${troutSpp.join(troutSpp.length === 2 ? ' and ' : ', ')}.`
            : 'No interior or eastern native trout species have been recorded in this subwatershed.'}
        </Text>
      </Box>

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
        may include state-listed threatened and endangered species. Trout
        species presence is based on occurrences of Apache, brook, bull,
        cutthroat, Gila, lake, and redband trout species. Species information is
        very incomplete and only includes species that have been identified by
        available data sources for this subwatershed. These species may or may
        not be directly impacted by this barrier. The absence of species in the
        available data does not necessarily indicate the absence of species in
        the subwatershed.
      </Paragraph>
    </Box>
  )
}

SpeciesWatershedPresence.propTypes = {
  barrierType: PropTypes.string.isRequired,
  ...SpeciesWatershedPresencePropTypeStub,
  sx: PropTypes.object,
}

SpeciesWatershedPresence.defaultProps = {
  ...SpeciesWatershedPresenceDefaultProps,
  sx: null,
}

export default SpeciesWatershedPresence
