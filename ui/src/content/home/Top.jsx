import React from 'react'
import { Box, Heading, Grid, Paragraph } from 'theme-ui'

import { Link } from 'components/Link'
import { HighlightBox } from 'components/Layout'

const Top = () => (
  <>
    <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
      Aquatic connectivity is essential. Fish and other aquatic organisms depend
      on high quality, connected river networks. A legacy of human use of river
      networks have left them fragmented by barriers such as dams and culverts.
      Fragmentation prevents species from dispersing and accessing habitats
      required for their persistence through changing conditions.
      <br />
      <br />
      Recently improved inventories of aquatic barriers enable us to describe,
      understand, and prioritize them for removal, restoration, and mitigation.
      Through this tool and others, we empower you by providing information on
      documented barriers and standardized methods by which to prioritize
      barriers of interest for restoration efforts.
    </Paragraph>

    <Box variant="boxes.section" sx={{ mt: '4rem' }}>
      <Heading as="h2">
        Enhancing aquatic connectivity by empowering people with actionable
        data:
      </Heading>

      <Grid columns={[0, 3]} gap={3} sx={{ mt: '2rem' }}>
        <HighlightBox title="Inventory" icon="dam">
          The aquatic barrier inventory is the foundation for identifying and
          prioritizing aquatic connectivity projects with partners. It provides
          essential information about the location, status, and characteristics
          of potential aquatic barriers.
          <br />
          <br />
          Scroll down for more information.
        </HighlightBox>

        <HighlightBox title="Prioritization" icon="prioritize">
          In order to maximize partner effort and return on investment, aquatic
          barriers are prioritized based on their contribution to the aquatic
          network if removed. Quantitative metrics provide actionable
          information to assist barrier removal projects.
          <br />
          <br />
          <Link to="/scoring_methods">Read more...</Link>
        </HighlightBox>

        <HighlightBox title="Teams" icon="team">
          Aquatic connectivity teams make barrier removal projects a reality. By
          combining effort across organizations and jurisdictions, partners work
          together to identify, prioritize, and implement barrier removal
          projects.
          <br />
          <br />
          <Link to="/regions/southeast/teams">
            Learn more about Southeast Aquatic Connectivity Teams
          </Link>
        </HighlightBox>
      </Grid>
    </Box>
  </>
)

export default Top
