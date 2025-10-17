import React from 'react'
import { Box, Heading, Grid, Image, Paragraph, Text, Divider } from 'theme-ui'

import { siteMetadata } from 'config'
import { Link, OutboundLink } from 'components/Link'
import { HighlightBox } from 'components/Layout'

const { naccURL } = siteMetadata

const AboutNACC = () => (
  <Box variant="boxes.section">
    <Heading as="h2">
      National Aquatic Connectivity Collaborative
      <br />
      <Box sx={{ fontSize: [3, 4], mt: '0.5rem' }}>
        Enhancing aquatic connectivity by empowering people with actionable data
      </Box>
    </Heading>

    <Grid columns={[0, 3]} gap={3} sx={{ mt: '2rem' }}>
      <HighlightBox title="Inventory" icon="dam">
        The aquatic barrier inventory is the foundation for identifying and
        prioritizing aquatic connectivity projects with partners. It provides
        essential information about the location, status, and characteristics of
        potential aquatic barriers.
        <br />
        <br />
        <OutboundLink to={`${naccURL}/inventory/`}>
          Learn more about the inventory
        </OutboundLink>
        .
      </HighlightBox>

      <HighlightBox title="Prioritization" icon="prioritize">
        In order to maximize partner effort and return on investment, aquatic
        barriers are prioritized based on their contribution to the aquatic
        network if removed. Quantitative metrics provide actionable information
        to assist barrier removal projects.
        <br />
        <br />
        <Link to="/scoring_methods">Read more about the methods here...</Link>
      </HighlightBox>

      <HighlightBox title="Teams" icon="team">
        Aquatic connectivity teams make barrier removal projects a reality. By
        combining effort across organizations and jurisdictions, partners work
        together to identify, prioritize, and implement barrier removal
        projects.
        <br />
        <br />
        <OutboundLink to={`${naccURL}/teams/`}>
          Learn more about Aquatic Connectivity Teams
        </OutboundLink>
        .
      </HighlightBox>
    </Grid>
    <Paragraph varaint="paragraph.large" sx={{ mt: '2rem' }}>
      <OutboundLink to={naccURL}>
        Learn more about the National Aquatic Connectivity Collabrative
      </OutboundLink>{' '}
      and explore{' '}
      <OutboundLink to={naccURL}>Frequently Asked Questions</OutboundLink> about
      it.
    </Paragraph>
  </Box>
)

export default AboutNACC
