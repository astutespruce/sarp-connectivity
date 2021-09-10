import React from 'react'
import PropTypes from 'prop-types'
import { Box, Button, Flex, Grid, Text } from 'theme-ui'
import { ChartBar, SearchLocation } from '@emotion-icons/fa-solid'

import { Link } from 'components/Link'

const RegionActionLinks = ({ region }) => (
  <Grid
    columns={2}
    gap={5}
    sx={{
      mt: '4rem',
      py: '1rem',
      px: '1rem',
      bg: 'grey.1',
      borderTop: '1px solid',
      borderTopColor: 'grey.3',
      borderBottom: '1px solid',
      borderBottomColor: 'grey.3',
    }}
  >
    <Box
      sx={{
        borderRight: '1px solid',
        borderRightColor: '#FFF',
        px: '2rem',
        width: '100%',
      }}
    >
      <Text>Want to explore summary statistics in an interative map?</Text>
      <Flex sx={{ justifyContent: 'center', mt: '1rem' }}>
        <Link to="/summary">
          <Button variant="primary">
            <ChartBar size="1em" />
            &nbsp; Start summarizing
          </Button>
        </Link>
      </Flex>
    </Box>
    <Box
      sx={{
        px: '2rem',
        width: '100%',
      }}
    >
      <Text>Want to prioritize barriers for further investigation?</Text>
      <Flex sx={{ justifyContent: 'center', mt: '1rem' }}>
        <Link to="/priority">
          <Button>
            <SearchLocation size="1em" />
            &nbsp; Start prioritizing
          </Button>
        </Link>
      </Flex>
    </Box>
  </Grid>
)

RegionActionLinks.propTypes = {
  region: PropTypes.string.isRequired,
}

export default RegionActionLinks
