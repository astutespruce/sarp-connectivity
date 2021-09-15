import React from 'react'
import PropTypes from 'prop-types'
import { Box, Heading, Grid, Paragraph } from 'theme-ui'

import { formatNumber } from 'util/format'

const has = (num) => (num === 1 ? 'has' : 'have')

const Species = ({ tespp, statesgcnspp, regionalsgcnspp, ...props }) => (
  <Box {...props}>
    <Heading as="h3">Species information</Heading>

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
        <b>
          {formatNumber(tespp)} federally-listed threatened and endangered
          aquatic species
        </b>{' '}
        {has(tespp)} been found in the subwatershed containing this barrier.
      </Box>
      <Box>
        <b>
          {statesgcnspp} state-listed aquatic Species of Greatest Conservation
          Need (SGCN)
        </b>{' '}
        {has(statesgcnspp)} been found in the subwatershed containing this
        barrier.
      </Box>
      <Box>
        <b>
          <b>{regionalsgcnspp}</b> regionally-listed aquatic species of greatest
          conservation need
        </b>{' '}
        {has(regionalsgcnspp)} been identified by available data sources for
        this subwatershed.
      </Box>
    </Grid>

    <Paragraph variant="help" sx={{ mt: '2rem' }}>
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
  tespp: PropTypes.number,
  statesgcnspp: PropTypes.number,
  regionalsgcnspp: PropTypes.number,
}

Species.defaultProps = {
  tespp: 0,
  statesgcnspp: 0,
  regionalsgcnspp: 0,
}

export default Species
