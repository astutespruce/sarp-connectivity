import React from 'react'
import { Box, Divider, Grid, Paragraph, Heading } from 'theme-ui'

import { Link } from 'components/Link'

const Regions = () => (
  <Box variant="boxes.section">
    <Divider sx={{ mb: '4rem' }} />
    <Heading as="h2" variant="heading.section">
      Explore the inventory by region:
    </Heading>

    <Grid columns={[0, '1fr 2fr']} gap={4} sx={{ mt: '2rem' }}>
      <Box sx={{ height: '8rem', width: '100%', bg: 'grey.1' }}>
        SARP region map image
      </Box>
      <Box>
        <Link to="/regions/southeast">
          <Heading as="h3" sx={{ fontWeight: 'normal' }}>
            Southeast region
          </Heading>
        </Link>
        <Paragraph>Brief overview / key stats</Paragraph>
      </Box>
    </Grid>

    <Grid columns={[0, '1fr 2fr']} gap={4} sx={{ mt: '3rem' }}>
      <Box sx={{ height: '8rem', width: '100%', bg: 'grey.1' }}>
        Mountain / Prairie region map image
      </Box>
      <Box>
        <Link to="/regions/great_plains_intermountain_west">
          <Heading as="h3" sx={{ fontWeight: 'normal' }}>
            Great Plains &amp; Intermountain West
          </Heading>
        </Link>
        <Paragraph>Brief overview / key stats</Paragraph>
      </Box>
    </Grid>

    <Grid columns={[0, '1fr 2fr']} gap={4} sx={{ mt: '3rem' }}>
      <Box sx={{ height: '8rem', width: '100%', bg: 'grey.1' }}>
        Southwest region map image
      </Box>
      <Box>
        <Link to="/regions/southwest">
          <Heading as="h3" sx={{ fontWeight: 'normal' }}>
            Southwest region
          </Heading>
        </Link>
        <Paragraph>Brief overview / key stats</Paragraph>
      </Box>
    </Grid>
  </Box>
)

export default Regions
