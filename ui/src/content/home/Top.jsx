import React from 'react'
import { Box, Heading, Grid, Image, Paragraph, Text } from 'theme-ui'

import { Link, OutboundLink } from 'components/Link'
import { HighlightBox } from 'components/Layout'
import SARPLogo from 'images/sarp_logo.png'
import NFHPLogo from 'images/nfhp_logo.svg'

const Top = () => (
  <>
    <Heading as="h2" sx={{ mt: '2rem' }}>
      Aquatic connectivity is essential
    </Heading>
    <Text sx={{ fontSize: ['1.25rem', 4], mt: '0.5rem' }}>
      Fish and other aquatic organisms depend on high quality, connected river
      networks. A legacy of human use of river networks have left them
      fragmented by barriers such as dams and culverts. Fragmentation prevents
      species from dispersing and accessing habitats required for their
      persistence through changing conditions.
    </Text>

    <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
      Recently improved inventories, brought to you by the{' '}
      <OutboundLink to="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
        Southeast Aquatic Resources Partnership
      </OutboundLink>{' '}
      (SARP) and partners, enable us to describe, understand, and prioritize
      aquatic barriers for removal, restoration, and mitigation. Through this
      tool and others, we empower you with information on documented barriers
      and standardized methods to prioritize barriers of interest for
      restoration efforts.
    </Paragraph>

    <Grid columns="3fr 1fr" gap={5} sx={{ mt: '2rem' }}>
      <Paragraph>
        This tool and inventory were made possible by funding from the{' '}
        <OutboundLink to="https://www.fws.gov/program/national-fish-passage">
          U.S. Fish and Wildlife Service
        </OutboundLink>
        ,{' '}
        <OutboundLink to="https://www.americanrivers.org/">
          American Rivers
        </OutboundLink>
        , the{' '}
        <OutboundLink to="https://www.nfwf.org/">
          National Fish and Wildlife Foundation
        </OutboundLink>
        ,{' '}
        <OutboundLink to="https://www.fs.usda.gov/">
          U.S. Forest Service
        </OutboundLink>
        , and state wildlife grant funding from Florida and Texas. This effort
        would not be possible without the collaboration of our partners from
        numerous state, federal, and non profit organizations as well as the{' '}
        <OutboundLink to="https://www.fishhabitat.org/">
          National Fish Habitat Partnership
        </OutboundLink>
        . Structures described within this inventory are maintained within
        databases housed by multiple entities and aggregated here for display
        and analysis.
      </Paragraph>
      <Box sx={{ maxWidth: '240px' }}>
        <Box>
          <OutboundLink to="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
            <Image src={SARPLogo} />
          </OutboundLink>
        </Box>
        <Box sx={{ mt: '2rem' }}>
          <OutboundLink to="">
            <Image src={NFHPLogo} />
          </OutboundLink>
        </Box>
      </Box>
    </Grid>
    <Paragraph sx={{ mt: '2rem' }}>
      National barrier datasets used in this inventory include the{' '}
      <OutboundLink to="https://nid.usace.army.mil/#/">
        National Inventory of Dams
      </OutboundLink>
      ,{' '}
      <OutboundLink to="https://www.usgs.gov/data/waterfalls-and-rapids-conterminous-united-states-linked-national-hydrography-datasets-v20">
        USGS Waterfalls of the Conterminous U.S.
      </OutboundLink>
      , and{' '}
      <OutboundLink to="https://www.usgs.gov/data/database-stream-crossings-united-states">
        USGS Database of Stream Crossings in the U.S.
      </OutboundLink>{' '}
      Barriers are snapped to aquatic networks derived from the{' '}
      <OutboundLink to="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution">
        USGS High Resolution National Hydrography Dataset
      </OutboundLink>{' '}
      supplemented with additional information from the{' '}
      <OutboundLink to="https://www.fws.gov/program/national-wetlands-inventory">
        National Wetlands Inventory
      </OutboundLink>
      .
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
