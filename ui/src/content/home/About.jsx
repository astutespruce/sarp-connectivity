import React from 'react'
import { Box, Flex, Grid, Image, Paragraph, Text } from 'theme-ui'

import { siteMetadata } from 'config'
import { OutboundLink } from 'components/Link'

import FlockProcessDamImage from 'images/28274676694_1840f44362_o.jpg'
import NumanaDamImage from 'images/53188100355_4ac3d174a8_o.jpg'
import GrahamCulvertImage from 'images/54791618987_56ea39a5db_o.jpg'
import DamRemovalTeamImage from 'images/Roaring_River_dam_removal_partners_small.jpg'
import USFWSLogo from 'images/usfws_logo.svg'
import USFSLogo from 'images/usfs_logo.svg'
import TNCLogo from 'images/tnc_logo.svg'
import AmericanRiversLogo from 'images/american_rivers_logo.svg'
import TULogo from 'images/trout_unlimited_logo.svg'

const { naccURL } = siteMetadata

const About = () => (
  <>
    <Text sx={{ mt: '4rem', fontSize: [4, 4, 5], fontWeight: 'bold' }}>
      Improve aquatic connectivity by prioritizing aquatic barriers for removal
      using the best available data
    </Text>

    <Paragraph sx={{ mt: '0.75rem' }}>
      Fish and other aquatic organisms depend on high quality, connected river
      networks. A legacy of human use of river networks have left them
      fragmented by barriers such as dams and culverts. Fragmentation prevents
      species from dispersing and accessing habitats required for their
      persistence through changing conditions.
      <br />
      <br />
      The <b>National Aquatic Barrier Inventory & Prioritization Tool</b> is
      part of the{' '}
      <b>
        <OutboundLink to={naccURL}>
          National Aquatic Connectivity Collaborative
        </OutboundLink>
      </b>{' '}
      (NACC), which is a national effort to build a community of practice of
      resource management partners working together to identify aquatic
      barriers, prioritize these barriers for removal or mitigation, and
      implement barrier removal projects across political boundaries.
      <br />
      <br />
      At the national scale, the National Aquatic Barrier Inventory and
      Prioritization Tool is made possible by funding from the{' '}
      <OutboundLink to="https://www.fws.gov/program/national-fish-passage">
        U.S. Fish and Wildlife Service
      </OutboundLink>
      ,{' '}
      <OutboundLink to="https://www.americanrivers.org/">
        American Rivers
      </OutboundLink>{' '}
      , the{' '}
      <OutboundLink to="https://www.nfwf.org/">
        National Fish and Wildlife Foundation
      </OutboundLink>
      ,{' '}
      <OutboundLink to="https://www.fs.usda.gov/">
        U.S. Department of Agriculture, Forest Service
      </OutboundLink>
      ,{' '}
      <OutboundLink to="https://www.nature.org/">
        The Nature Conservancy
      </OutboundLink>
      , <OutboundLink to="https://www.tu.org/">Trout Unlimited</OutboundLink>,{' '}
      and state wildlife grant funding from Florida and Texas. This effort would
      not be possible without the collaboration of our partners from numerous
      state, federal, and non profit organizations as well as the{' '}
      <OutboundLink to="https://www.fishhabitat.org/">
        National Fish Habitat Partnership
      </OutboundLink>
      .
    </Paragraph>

    <Flex
      sx={{
        mt: '2rem',
        gap: '1rem',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <Box>
        <OutboundLink to="https://www.fws.gov/program/national-fish-passage">
          <Image src={USFWSLogo} alt="USFWS logo" sx={{ height: '96px' }} />
        </OutboundLink>
      </Box>
      <Box>
        <OutboundLink to="https://www.fs.usda.gov/">
          <Image src={USFSLogo} alt="USFS logo" sx={{ height: '96px' }} />
        </OutboundLink>
      </Box>
      <Box>
        <OutboundLink to="https://www.nature.org/">
          <Image src={TNCLogo} alt="TNC logo" sx={{ width: '150px' }} />
        </OutboundLink>
      </Box>

      <Box>
        <OutboundLink to="https://www.americanrivers.org/">
          <Image
            src={AmericanRiversLogo}
            alt="American Rivers logo"
            sx={{ width: '140px' }}
          />
        </OutboundLink>
      </Box>

      <Box>
        <OutboundLink to="https://www.tu.org/">
          <Image
            src={TULogo}
            alt="Trout Unlimited logo"
            sx={{ height: '80px' }}
          />
        </OutboundLink>
      </Box>
    </Flex>

    <Grid columns={[0, '2fr 1fr']} gap={4} sx={{ mt: '4rem' }}>
      <Paragraph>
        This inventory is a growing and living database of dams, culverts, and
        other road crossings that spans all 50 states, Puerto Rico, and the US
        Virgin Islands, compiled by{' '}
        <OutboundLink to="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
          Southeast Aquatic Resources Partnership
        </OutboundLink>{' '}
        (SARP) with the generous support from many partners and funders. It
        integrates existing datasets from local, state, and federal partners
        with data collected from ongoing field surveys and local knowledge of
        specific structures.
      </Paragraph>
      <Box>
        <Image src={FlockProcessDamImage} alt="Flock Process dam" />
        <Text sx={{ fontSize: 0, color: 'grey.8' }}>
          Flock Process Dam, Connecticut. Removed in 2018, restoring over 4
          miles of stream access to diadromous species.{' '}
          <OutboundLink to="https://www.flickr.com/photos/usfwsnortheast/28274676694/in/album-72157650009434305">
            U.S. Fish and Wildlife Service Northeast Region
          </OutboundLink>
        </Text>
      </Box>
    </Grid>

    <Grid columns={[0, 3, 3]} sx={{ mt: '2rem' }}>
      <Box>
        <Image src={NumanaDamImage} alt="Numana Dam" />
        <Text sx={{ fontSize: 0, color: 'grey.8' }}>
          Numana Dam, Nevada. Fish passage structure project underway.{' '}
          <OutboundLink to="https://www.flickr.com/photos/usfws_pacificsw/53188100355/in/album-72177720310798426">
            N. Hurner, U.S. Fish and Wildlife Service
          </OutboundLink>
        </Text>
      </Box>

      <Box>
        <Image src={GrahamCulvertImage} alt="Culvert near Graham, WA" />
        <Text sx={{ fontSize: 0, color: 'grey.8' }}>
          Culvert near Graham, WA replaced in 2025 for fish passage.{' '}
          <OutboundLink to="https://www.flickr.com/photos/wsdot/54791618987/in/album-72177720329098004">
            Washington State Department of Transportation
          </OutboundLink>
        </Text>
      </Box>

      <Box>
        <Image src={DamRemovalTeamImage} alt="Roaring River Dam Removal" />
        <Text sx={{ fontSize: 0, color: 'grey.8' }}>
          Roaring River Dam Removal, Tennessee, 2017. Mark Thurman, Tennessee
          Wildlife Resources Agency.
        </Text>
      </Box>
    </Grid>

    <Paragraph sx={{ mt: '2rem' }}>
      In order to fill data gaps, partners have been inventorying barriers in
      the field from the bottom up, using a standardized protocol developed by
      the{' '}
      <OutboundLink to="https://streamcontinuity.org/">
        North Atlantic Aquatic Connectivity Collaborative
      </OutboundLink>{' '}
      (NAACC). The North Atlantic Aquatic Connectivity Collaborative (NAACC) is
      a network of individuals from universities, conservation organizations,
      and state and federal natural resource and transportation departments
      focused on improving aquatic connectivity across a thirteen-state region,
      from Maine to West Virginia. As this protocol has expanded across the
      country, partners from fifteen states within the southeastern region, as
      well as additional states in the Great Plains and Intermountain West have
      adopted this protocol, which will now be coordinated and managed at the
      National scale by the National Fish Habitat Partnership, now called the
      National Aquatic Connectivity Collaborative.
    </Paragraph>
  </>
)

export default About
