import React from 'react'
import PropTypes from 'prop-types'
import { Button, Flex, Grid, Text } from 'theme-ui'
import { ChartBar, Fish, SearchLocation } from '@emotion-icons/fa-solid'

import { Link } from 'components/Link'

const RegionActionLinks = ({ region }) => (
  <Grid
    columns={3}
    gap={3}
    sx={{
      mt: '4rem',
      py: '1rem',
      px: '1rem',
      bg: 'blue.1',
      borderTop: '1px solid',
      borderTopColor: 'grey.3',
      borderBottom: '1px solid',
      borderBottomColor: 'grey.3',
    }}
  >
    <Flex
      sx={{
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: '1rem',
        borderRight: '1px solid',
        borderRightColor: '#FFF',
        px: '1rem',
        width: '100%',
        height: '100%',
      }}
    >
      <Text sx={{ flex: '0 0 auto' }}>
        Explore how many dams or road-related barriers there are in a state,
        county, or watershed.
      </Text>
      <Flex
        sx={{
          flex: '1 1 auto',
          justifyContent: 'center',
          alignItems: 'flex-end',
        }}
      >
        <Link to={`/explore/?region=${region}`}>
          <Button variant="primary">
            <ChartBar size="1em" />
            &nbsp; Start exploring
          </Button>
        </Link>
      </Flex>
    </Flex>

    <Flex
      sx={{
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: '1rem',
        borderRight: '1px solid',
        borderRightColor: '#FFF',
        px: '1rem',
        width: '100%',
        height: '100%',
      }}
    >
      <Text sx={{ flex: '0 0 auto' }}>
        Explore dams and road-related barriers that have been removed or
        mitigated by state, county, or watershed.
      </Text>
      <Flex
        sx={{
          flex: '1 1 auto',
          justifyContent: 'center',
          alignItems: 'flex-end',
        }}
      >
        <Link to={`/restoration/?region=${region}`}>
          <Button variant="primary">
            <Fish size="1em" />
            &nbsp; See restoration progress
          </Button>
        </Link>
      </Flex>
    </Flex>

    <Flex
      sx={{
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: '1rem',
        px: '1rem',
        width: '100%',
        height: '100%',
      }}
    >
      <Text sx={{ flex: '0 0 auto' }}>
        Identify and rank dams or road-related barriers that reconnect the most
        high-quality aquatic networks.
      </Text>
      <Flex
        sx={{
          flex: '1 1 auto',
          justifyContent: 'center',
          alignItems: 'flex-end',
        }}
      >
        <Link to="/priority">
          <Button>
            <SearchLocation size="1em" />
            &nbsp; Start prioritizing
          </Button>
        </Link>
      </Flex>
    </Flex>
  </Grid>
)

RegionActionLinks.propTypes = {
  region: PropTypes.string.isRequired,
}

export default RegionActionLinks
