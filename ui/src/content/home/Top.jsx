import React from 'react'
import { Box, Flex, Heading, Grid, Image, Paragraph, Text } from 'theme-ui'

import { Link, OutboundLink } from 'components/Link'
import { HighlightBox } from 'components/Layout'
import SARPLogo from 'images/sarp_logo.png'
import NFHPLogo from 'images/nfhp_logo.svg'
import AmericanRiversLogo from 'images/american_rivers_logo.svg'
import TULogo from 'images/trout_unlimited_logo.svg'
import USFSLogo from 'images/usfs_logo.svg'
import USFWSLogo from 'images/usfws_logo.svg'

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
    <Paragraph sx={{ mt: '2rem' }}>
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
        U.S. Department of Agriculture, Forest Service
      </OutboundLink>
      , and state wildlife grant funding from Florida and Texas. This effort
      would not be possible without the collaboration of our partners from
      numerous state, federal, and non profit organizations such as{' '}
      <OutboundLink to="https://www.tu.org/">Trout Unlimited</OutboundLink> and{' '}
      <OutboundLink to="https://www.nature.org/">
        The Nature Conservancy
      </OutboundLink>
      , as well as the{' '}
      <OutboundLink to="https://www.fishhabitat.org/">
        National Fish Habitat Partnership
      </OutboundLink>
      .
    </Paragraph>

    <Flex
      sx={{
        mt: '2rem',
        alignItems: 'center',
        gap: '1rem',
        justifyContent: 'space-between',
      }}
    >
      <OutboundLink to="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
        <Image src={SARPLogo} sx={{ width: '200px' }} />
      </OutboundLink>
      <Box sx={{ flex: '0 0 auto', mt: '1rem' }}>
        <OutboundLink to="https://www.fws.gov/program/national-fish-passage">
          <Image src={USFWSLogo} sx={{ height: '96px' }} />
        </OutboundLink>
      </Box>
      <Box sx={{ flex: '0 0 auto', mt: '1rem' }}>
        <OutboundLink to="https://www.fs.usda.gov/">
          <Image src={USFSLogo} sx={{ height: '96px' }} />
        </OutboundLink>
      </Box>
      <Box sx={{ flex: '0 0 auto', mt: '1rem' }}>
        <OutboundLink to="https://fishhabitat.org/">
          <Image src={NFHPLogo} sx={{ width: '200px' }} />
        </OutboundLink>
      </Box>
      <Box sx={{ flex: '0 0 auto', mt: '1rem' }}>
        <OutboundLink to="https://www.americanrivers.org/">
          <Image src={AmericanRiversLogo} sx={{ width: '140px' }} />
        </OutboundLink>
      </Box>

      <Box sx={{ flex: '0 0 auto', mt: '1rem' }}>
        <OutboundLink to="https://www.tu.org/">
          <Image src={TULogo} sx={{ height: '80px' }} />
        </OutboundLink>
      </Box>
    </Flex>
    <Paragraph sx={{ mt: '3rem' }}>
      In addition to state and local datasets, national barrier datasets used in
      this inventory include the{' '}
      <OutboundLink to="https://nid.sec.usace.army.mil/#/">
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
      . Along with national data sources, several other regional and state
      efforts to collect barrier data were included in this inventory and are
      regularly updated within. To see a list of data sources as well as a link
      to submit a missing data source,{' '}
      <OutboundLink to="https://docs.google.com/document/d/1mUwk9rHukmY1D_NInxjdIxbBVfILD1Y8Xr-lMqjV4xU/edit?usp=sharing">
        click here
      </OutboundLink>
      .
      <br />
      <br />
      This inventory and prioritization tool are planned for a full national
      expansion by the end of 2025. Barriers for Alaska, Nevada, California, the
      Great Lakes Region, and the Northeast Region are currently incomplete.
      <br />
      <br />
      This inventory and prioritization tool is designed to guide users in
      identifying high priority barrier removal projects. To access information
      about to funding sources for barrier removal, please visit the{' '}
      <OutboundLink to="https://interagency-bil-fish-passage-project-1-fws.hub.arcgis.com/">
        Fish Passage Portal
      </OutboundLink>
      . The portal is a &quot;one-stop shop&quot; for anyone who needs
      information, funding, or resources to improve fish passage and aquatic
      connectivity projects. It provides landowners and public lands managers
      the tools to find funding across the federal government, as well as access
      to data, planning, and geospatial information.
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
          Scroll down to learn more about the inventory.
        </HighlightBox>

        <HighlightBox title="Prioritization" icon="prioritize">
          In order to maximize partner effort and return on investment, aquatic
          barriers are prioritized based on their contribution to the aquatic
          network if removed. Quantitative metrics provide actionable
          information to assist barrier removal projects.
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
          Learn more about Aquatic Connectivity Teams by choosing a region from{' '}
          <b>Explore regions</b> at the top. To join a team click{' '}
          <OutboundLink to="https://www.americanrivers.org/aquatic-connectivity-groups/">
            here
          </OutboundLink>
          .
        </HighlightBox>
      </Grid>
    </Box>
  </>
)

export default Top
