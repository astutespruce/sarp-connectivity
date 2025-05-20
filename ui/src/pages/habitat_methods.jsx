import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import {
  Box,
  Container,
  Divider,
  Grid,
  Paragraph,
  Heading,
  Text,
} from 'theme-ui'

import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Link, OutboundLink } from 'components/Link'

const HabitatMethodsPage = ({
  data: {
    headerImage,
    pnwSalmonImage: {
      childImageSharp: { gatsbyImageData: pnwSalmonImage },
    },
    pswSalmonImage: {
      childImageSharp: { gatsbyImageData: pswSalmonImage },
    },
    brookTroutImage: {
      childImageSharp: { gatsbyImageData: brookTroutImage },
    },
    brookTroutImage2: {
      childImageSharp: { gatsbyImageData: brookTroutImage2 },
    },
    sturgeonImage: {
      childImageSharp: { gatsbyImageData: sturgeonImage },
    },
    apacheTroutImage: {
      childImageSharp: { gatsbyImageData: apacheTroutImage },
    },
    coastalCutthroatTroutImage: {
      childImageSharp: { gatsbyImageData: coastalCutthroatTroutImage },
    },
    coloradoRiverCutthroatTroutImage: {
      childImageSharp: { gatsbyImageData: coloradoRiverCutthroatTroutImage },
    },
    lahontanCutthroatTroutImage: {
      childImageSharp: { gatsbyImageData: lahontanCutthroatTroutImage },
    },
  },
}) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      height="30vh"
      minHeight="18rem"
      //   credits={{
      //     author: 'Brandon',
      //     url: 'https://unsplash.com/photos/gray-fish-on-water-during-daytime-enPHTN3OPRw',
      //   }}
    />

    <Container>
      <Heading as="h1">Aquatic Species Habitat Methods</Heading>
      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        Instream habitat data for key species and species groups were compiled
        from regional partners and associated with the{' '}
        <OutboundLink to="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution">
          National Hydrography Dataset - High Resolution Plus
        </OutboundLink>{' '}
        (NHDPlusHR) dataset from the U.S. Geological Survey, which is used to{' '}
        <Link to="/network_methods">create the aquatic networks</Link> used in
        this tool. Our overall goal is to estimate the amount of species-level
        habitat that could be gained by removing or mitgating a specific barrier
        based on the best available species data and standardized aquatic
        network data.
        <br />
        <br />
        These estimates are intended to be a starting point for exploring and
        prioritizing barriers from a species perspective rather than the total
        upstream or downstream functional networks, which may greatly
        overestimate the amount of habitat that could be made available to
        particular species.
      </Paragraph>
      <Paragraph sx={{ mt: '2rem' }} variant="help">
        Please note: these estimates should be used with caution due to the many
        inherent limitations of species habitat data, including incomplete
        coverage of the current or potential distribution of a species, lack of
        data within particular stream reaches, incorrect attribution of stream
        reaches to habitat, or simplistic elevation gradient rules used to
        define maximum extents of species habitat. Furthermore, the methods
        below attribute habitat to entire NHDPlusHR flowlines without
        considering elevation gradients or other natural barriers that would
        prevent the dispersal of aquatic organisms, and may both over and
        underestimate actual habitat for these species and species groups.
        <br />
        <br />
        If you find a major error in the habitat lengths associated with
        barriers in this tool, please{' '}
        <a href="mailto:Kat@southeastaquatics.net">contact us</a>.
      </Paragraph>

      <Box sx={{ mt: '2rem' }}>
        <Heading as="h3">Table of contents:</Heading>
        <Box
          as="ul"
          sx={{
            mt: '0.5rem',
            lineHeight: 1.2,
          }}
        >
          <li>
            <a href="#StreamNet">
              Pacific Northwest Anadromous and Resident Fish Species Habitat
            </a>
          </li>
          <li>
            <a href="#CABaseline">California Baseline Fish Habitat</a>
          </li>
          <li>
            <a href="#EasternBrookTrout">Eastern Brook Trout Habitat</a>
          </li>
          <li>
            <a href="#Northeast">
              Chesapeake Bay Watershed Diadromous Fish Habitat
            </a>
          </li>
          <li>
            <a href="#SARP">Southeast Diadromous Fish Habitat</a>
          </li>
          <li>
            <a href="#ApacheTrout">Apache & Gila Trout</a>
          </li>
          <li>
            <a href="#LahontanCutthroatTrout">Lahontan cutthroat trout</a>
          </li>
          <li>
            <a href="#CoastalCutthroatTrout">
              Coastal Cutthroat Trout (California)
            </a>
          </li>
          <li>
            <a href="#ColoradoRiverCutthroatTrout">
              Colorado River Cutthroat Trout (California)
            </a>
          </li>
        </Box>
      </Box>

      <Divider />

      <Box id="StreamNet" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Pacific Northwest Anadromous and Resident Fish Species Habitat
        </Heading>
        <Grid columns="2fr 1fr" gap={4}>
          <Paragraph>
            Known current (not potential) instream habitat data for key
            anadromous and resident fish species in Washington, Oregon, Idaho,
            and Montana were derived from{' '}
            <OutboundLink to="https://www.streamnet.org/home/data-maps/gis-data-sets/">
              StreamNet
            </OutboundLink>{' '}
            (January 2019 version). These habitat data are compiled by StreamNet
            from partners within the region and are attributed to stream
            segments within a common regional mixed-scale hydrography dataset,
            and may include segments that are used for one or more life stages
            such as spawning or migration.
          </Paragraph>
          <Box>
            <GatsbyImage
              image={pnwSalmonImage}
              alt="Salmon at Wildwood Recreation Site"
            />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Salmon |{' '}
              <OutboundLink to="https://www.flickr.com/photos/blmoregon/52633917843/in/album-72177720303743258/">
                Bureau of Land Management Oregon & Washington
              </OutboundLink>
            </Text>
          </Box>
        </Grid>
        <Heading as="h4" sx={{ mt: '1rem' }}>
          Species included:
        </Heading>
        <Grid
          columns={3}
          gap={3}
          sx={{ mt: '0.5rem', 'li+li': { mt: '0.1rem' } }}
        >
          <Box as="ul">
            <li>Bonneville cutthroat trout</li>
            <li>Bull trout</li>
            <li>Chinook salmon</li>
            <li>Chum salmon</li>
            <li>Coastal cutthroat trout</li>
            <li>Coho salmon</li>
          </Box>
          <Box as="ul">
            <li>
              Green sturgeon<sup>*</sup>
            </li>
            <li>Kokanee</li>
            <li>
              Pacific lamprey<sup>*</sup>
            </li>
            <li>Pink salmon</li>
            <li>Rainbow trout</li>
            <li>Redband trout</li>
          </Box>
          <Box as="ul">
            <li>Sockeye salmon</li>
            <li>Steelhead</li>
            <li>Westslope cutthroat trout</li>
            <li>White sturgeon</li>
            <li>Yellowstone cutthroat trout</li>
          </Box>
        </Grid>
        <Paragraph variant="help" sx={{ lineHeight: 1, mt: '0.5rem' }}>
          <sup>*</sup> only available for subset of range.
        </Paragraph>

        <Paragraph sx={{ mt: '3rem', fontWeight: 'bold' }}>
          We used the following steps to attribute StreamNet species habitat
          data for each species to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>
            Merged linework to aggregate all life stages into a single set of
            linework and then split back into individual segments.
          </li>
          <li>
            Identified and filled gaps (&lt;5 meters) between the endpoints of
            nearby lines; these were most likely the result of processing errors
            and different vintages of underlying hydrography used in the
            StreamNet data.
          </li>
          <li>
            Identified related groups of habitat lines that were within 1
            kilometer of each other; these groups are used to determine when to
            fill gaps in the species habitat linework.
          </li>
          <li>Dropped any line segments &lt; 1 meter in length.</li>
          <li>
            Dropped any line segments well outside species range; these were
            most likely the result of processing or attribution errors.
          </li>
          <li>
            Selected NHDPlusHR flowlines that intersect a 50 meter buffer around
            habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches, network loops, or
            occurred between distinct groups of species habitat. The remaining
            flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 50 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 65%
            of its length is within the buffer, it overlaps by at least 10
            meters, and the total amount of overlap is less than 500 meters
            different from its total length. Any fragments that have high
            overlap with the buffer but are less than 150 meters in length were
            dropped unless they are headwaters or connect to upstream segments
            already marked as habitat.
          </li>
          <li>
            The outputs of steps 8 and 9 are used to define anchor points in a
            network analysis to fill gaps between segments identified as
            habitat. We created a linear directed graph facing downstream using
            the NHDPlusHR network toplogy (excluding any network loops) and
            traversed this graph from the anchor points to upstream points of
            disconnected habitat linework (gaps must be less than 100 flowlines
            long). We selected flowlines identified from traversing these
            networks to fill gaps if they did not bridge distinct habitat groups
            and had at least 50% overlap with a 100 meter buffer around the
            habitat linework.
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence. For most species, the overall
            linework was similar and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the StreamNet data, attributed at the entire
          NHDPlusHR flowline level; it does not include elevation gradients or
          other natural barriers that may have been included within the original
          data.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="CABaseline" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          California Baseline Fish Habitat
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            <Paragraph>
              Known current and potential instream habitat data for key
              anadromous species and resident resident rainbow trout (Southern
              California) were derived from the
              <OutboundLink to="https://psmfc.maps.arcgis.com/home/item.html?id=a8117ce44a16493ca2aa0571769e5654">
                California Baseline Fish Habitat
              </OutboundLink>{' '}
              dataset (version 3) provided by the{' '}
              <OutboundLink to="https://www.cafishpassageforum.org/">
                California Fish Passage Forum
              </OutboundLink>
              . This dataset attributed habitat data to the NHDPlus v2.1
              medium-resolution hydrography, and aggregates all included species
              together into a single habitat dataset. This dataset is focused on
              estimating habitat for anadromous species and thus does not
              include full coverage of resident species across California.
            </Paragraph>
          </Box>

          <Box>
            <GatsbyImage
              image={pswSalmonImage}
              alt="Coho salmon spawning in the Salmon River, 2015"
            />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Coho salmon |{' '}
              <OutboundLink to="https://www.flickr.com/photos/usfws_pacificsw/52706030122/in/album-72177720301505972/">
                U.S. Fish and Wildlife Service Pacific Southwest Region
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the California Baseline Fish
          Habitat data to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>Merged line segments by ReachCode.</li>
          <li>
            Selected NHDPlusHR flowlines that have the same ReachCode as the
            habitat linework and overlapped the corresponding reaches in the
            habitat linework by at least 75% of their length and where their
            endpoints were within 1 kilometer of the nearest point in the
            habitat linework, and marked these as habitat. This was done to
            prevent including flowlines that had corresponding ReachCode values
            but represented grossly different actual stream reaches.
          </li>
          <li>
            Selected NHDPlusHR flowlines that intersected a 50 meter buffer
            around the habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches, network loops, or
            occurred between distinct groups of species habitat. The remaining
            flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 50 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 65%
            of its length is within the buffer, it overlaps by at least 10
            meters, and the total amount of overlap is less than 500 meters
            different from its total length. Any fragments that have high
            overlap with the buffer but are less than 150 meters in length were
            dropped unless they are headwaters or connect to upstream segments
            already marked as habitat.
          </li>
          <li>
            The outputs of steps 1, 4, and 5 are used to define anchor points in
            a network analysis to fill gaps between segments identified as
            habitat. We created a linear directed graph facing downstream using
            the NHDPlusHR network toplogy (excluding any network loops and
            canals / ditches) and traversed this graph from the anchor points to
            upstream points of disconnected habitat linework (gaps must be less
            than 100 flowlines long). We selected flowlines identified from
            traversing these networks to fill gaps if they did not bridge
            distinct habitat groups and had at least 50% overlap with a 200
            meter buffer around the habitat linework. (the larger tolerance was
            required due to the low resolution of NHDPlus in some areas)
          </li>
          <li>
            We then filled gaps between habitat segments identified above and
            the ocean, if the total gap was less than 10 kilometers.
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the California Baseline Fish Habitat dataset,
          attributed at the entire NHDPlusHR flowline level; it does not include
          elevation gradients or other natural barriers that may have been
          included within the California Baseline Fish Habitat dataset.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="EasternBrookTrout" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Eastern Brook Trout Habitat
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            <Paragraph>
              Eastern brook trout habitat data were derived from nonpublic data
              provided by Trout Unlimited. These data are based on NHDPlus
              medium-resolution flowlines that intersect with brook trout
              population patches, which were compiled from assessments by Trout
              Unlimited (2017-2022). These data are intended to provide a best
              guess estimate of brook trout instream habitat based on available
              data.
            </Paragraph>
          </Box>

          <Box>
            <GatsbyImage image={brookTroutImage} alt="Eastern Brook Trout" />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Eastern Brook Trout |{' '}
              <OutboundLink to="https://www.flickr.com/photos/usfwsnortheast/4752172480/in/gallery-144603962@N07-72157719171281455/">
                U.S. Fish and Wildlife Service Northeast Region
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the eastern brook trout
          habitat data to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>Merged line segments by ReachCode.</li>
          <li>
            Selected NHDPlusHR flowlines that have the same ReachCode as the
            habitat linework and overlapped the corresponding reaches in the
            habitat linework by at least 75% of their length and where their
            endpoints were within 2 kilometer of the nearest point in the
            habitat linework, and marked these as habitat. This was done to
            prevent including flowlines that had corresponding ReachCode values
            but represented grossly different actual stream reaches.
          </li>
          <li>
            Discarded any of the above flowlines that are coded by NHDPlusHR as
            intermittent and where either endpoint is greater than 250 meters
            from the nearest point on the habitat linework.
          </li>
          <li>
            Selected NHDPlusHR flowlines that intersected a 100 meter buffer
            around the habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches, network loops, or
            occurred between distinct groups of species habitat. The remaining
            flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 100 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 65%
            of its length is within the buffer, it overlaps by at least 10
            meters, and the total amount of overlap is less than 1 kilometer
            different from its total length. Any flowlines where either endpoint
            is greater than 2 kilometers from the nearest point on the habitat
            line work or any intermittent segments where the distance from
            either endpoint to the nearest point on the habitat linework is
            greater than 250 meters are discarded. Any fragments that have high
            overlap with the buffer but are less than 300 meters in length were
            dropped unless they are headwaters or connect to upstream segments
            already marked as habitat.
          </li>
          <li>
            The outputs of steps 1, 6, and 7 are used to define anchor points in
            a network analysis to fill gaps between segments identified as
            habitat. We created a linear directed graph facing downstream using
            the NHDPlusHR network toplogy (excluding any network loops and
            canals / ditches) and traversed this graph from the anchor points to
            upstream points of disconnected habitat linework (gaps must be less
            than 100 flowlines long). We selected flowlines identified from
            traversing these networks to fill gaps if they did not bridge
            distinct habitat groups and had at least 50% overlap with a 300
            meter buffer around the habitat linework. (the larger tolerance was
            required due to the low resolution of NHDPlus in some areas)
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the eastern brook trout habitat data, attributed at
          the entire NHDPlusHR flowline level; it does not include elevation
          gradients or other natural barriers that may have been included within
          the original data.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="Northeast" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Chesapeake Bay Watershed Diadromous Fish Habitat
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            <Paragraph>
              Habitat for several diadromous species in the Chesapeake Bay
              Watershed were derived from data provided by the Chesapeake Fish
              Passage Workgroup. These data were attributed to either NHDPlus
              medium-resolution flowlines or NHDPlusHR flowlines.
            </Paragraph>
          </Box>

          <Box>
            <GatsbyImage image={brookTroutImage2} alt="Eastern Brook Trout" />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Eastern Brook Trout |{' '}
              <OutboundLink to="https://www.flickr.com/photos/usfwsnortheast/8574372559/in/gallery-144603962@N07-72157719171281455/">
                U.S. Fish and Wildlife Service Northeast Region
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Heading as="h4" sx={{ mt: '1rem' }}>
          Species included:
        </Heading>
        <Grid
          columns={3}
          gap={3}
          sx={{ mt: '0.5rem', 'li+li': { mt: '0.1rem' } }}
        >
          <Box as="ul">
            <li>Alewife</li>
            <li>American eel</li>
            <li>American shad</li>
          </Box>
          <Box as="ul">
            <li>Atlantic sturgeon</li>
            <li>Blueback herring</li>
            <li>Brook trout</li>
          </Box>
          <Box as="ul">
            <li>Hickory shad</li>
            <li>Shortnose sturgeon</li>
            <li>Striped bass</li>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the Chesapeake Bay Watershed
          diadromous fish habitat data for each species to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>Merged line segments by ReachCode.</li>
          <li>
            Selected NHDPlusHR flowlines that have the same ReachCode as the
            habitat linework and overlapped the corresponding reaches in the
            habitat linework by at least 75% of their length and where their
            endpoints were within 2 kilometer of the nearest point in the
            habitat linework, and marked these as habitat. This was done to
            prevent including flowlines that had corresponding ReachCode values
            but represented grossly different actual stream reaches.
          </li>
          <li>
            Discarded any of the above flowlines that are coded by NHDPlusHR as
            intermittent and where either endpoint is greater than 500 meters
            from the nearest point on the habitat linework.
          </li>
          <li>
            Selected NHDPlusHR flowlines that intersected a 50 meter buffer
            around the habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches, network loops, or
            occurred between distinct groups of species habitat. The remaining
            flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 50 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 65%
            of its length is within the buffer, it overlaps by at least 10
            meters, and the total amount of overlap is less than 1 kilometer
            different from its total length. Any flowlines where either endpoint
            is greater than 2 kilometers from the nearest point on the habitat
            line work are discarded. Any fragments that have high overlap with
            the buffer but are less than 150 meters in length were dropped
            unless they are headwaters or connect to upstream segments already
            marked as habitat.
          </li>
          <li>
            The outputs of steps 1, 6, and 7 are used to define anchor points in
            a network analysis to fill gaps between segments identified as
            habitat. We created a linear directed graph facing downstream using
            the NHDPlusHR network toplogy (excluding any network loops and
            canals / ditches) and traversed this graph from the anchor points to
            upstream points of disconnected habitat linework (gaps must be less
            than 100 flowlines long). We selected flowlines identified from
            traversing these networks to fill gaps if they did not bridge
            distinct habitat groups and had at least 10% overlap with a 200
            meter buffer around the habitat linework.
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the Chesapeake Bay Watershed diadromous habitat data,
          attributed at the entire NHDPlusHR flowline level; it does not include
          elevation gradients or other natural barriers that may have been
          included within the original habitat data.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="SARP" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Southeast Diadromous Fish Habitat
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            <Paragraph>
              Diadromous fish habitat for the Southeast region was derived from
              data developed by the Southeast Aquatic Resources partnership.
              These data are based on an analysis of NHDPlus High Resolution
              flowlines in networks that flow into marine areas and have no dams
              downstream. SARP&apos;s methods included an analysis of element
              occurrence data for key diadromous species in the Southeast along
              with rules to determine possible habitat based on stream order.
              <br />
              <br />
              NOTE: this is an early draft of this habitat dataset, which is
              currently undergoing review by stakeholders and expected to be
              improved in subsequent versions.
            </Paragraph>
          </Box>

          <Box>
            <GatsbyImage image={sturgeonImage} alt="Gulf sturgeon" />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Gulf Sturgeon |{' '}
              <OutboundLink to="https://www.flickr.com/photos/usfwsendsp/6359207695/in/album-72157625204217622/">
                Kayla Kimmel, U.S. Fish and Wildlife Service
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the Southeast diadromous fish
          habitat data to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>
            Because these data were derived from networks based on NHDPlus High
            Resolution flowlines developed elsewhere in this tool, all network
            segments included NHDPlusID identifiers. We simply joined the
            diadromous habitat back to full flowlines based on NHDPlusID.
            <br />
            <br />
            However, where the upper end of habitat was based on the
            most-downstream dam on a given network, attributing at the flowline
            caused the habitat to extend a short distance upstream of the dam to
            the upper end of the flowline. This is a known issue with the
            methods here that attribute to the entire flowline level.
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the Southeast diadromous fish habitat data,
          attributed at the entire NHDPlusHR flowline level; it does not include
          elevation gradients or other natural barriers that may have been
          included within the original data.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="ApacheTrout" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Apache & Gila Trout Habitat
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            Apache trout habitat data were derived from data provided by Dan
            Dauwalter (Trout Unlimited) and Zachary Jackson (U.S. Fish and
            Wildlife Service) and Gila trout habitat data were derived from data
            provided by Dan Dauwalter (Trout Unlimited).
          </Box>

          <Box>
            <GatsbyImage image={apacheTroutImage} alt="Apache Trout" />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Apache Trout |{' '}
              <OutboundLink to="https://www.fws.gov/media/apache-trout">
                U.S. Fish and Wildlife Service
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the Apache and Gila trout
          habitat data to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>
            Selected NHDPlusHR flowlines that intersected a 50 meter buffer
            around the habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches or network loops. The
            remaining flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 50 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 50%
            of its length is within the buffer and the total amount of overlap
            is less than 1 kilometer different from its total length, or if its
            upstream endpoint is within 1 meter of the habitat linework and has
            at least 25% overlap. Any Any fragments that have high overlap with
            the buffer but are less than 150 meters in length were dropped
            unless they are headwaters or connect to upstream segments already
            marked as habitat.
          </li>
          <li>
            We manually selected NHD flowlines that were not otherwise selected
            above if they had a suitable amount of visual overlap and landscape
            position suggested that habitat could be extended to their entire
            lengths.
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the Apache and Gila trout habitat data, attributed at
          the entire NHDPlusHR flowline level; it does not include elevation
          gradients or other natural barriers that may have been included within
          the original data.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="LahontanCutthroatTrout" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Lahontan Cutthroat Trout Habitat
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            <Paragraph>
              Lahontan cutthroat trout habitat data were derived from data
              provided by Trout Unlimited. Data appear to have been developed
              based on an older version of NHDPlus High Resolution and were very
              close to the latest available NHDPlus High Resolution flowlines.
            </Paragraph>
          </Box>

          <Box>
            <GatsbyImage
              image={lahontanCutthroatTroutImage}
              alt="Lahontan Cutthroat Trout"
            />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Lahontan Cutthroat Trout |{' '}
              <OutboundLink to="https://www.fws.gov/media/lahontan-cutthroat-trout-7">
                Chad Mellison, U.S. Fish and Wildlife Service
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the Lahontan cutthroat trout
          habitat data to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>
            Selected NHDPlusHR flowlines that intersected a 10 meter buffer
            around the habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches or network loops. The
            remaining flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 50 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 50%
            of its length is within the buffer and the total amount of overlap
            is less than 1 kilometer different from its total length, or if its
            upstream endpoint is within 1 meter of the habitat linework and has
            at least 25% overlap. Any Any fragments that have high overlap with
            the buffer but are less than 150 meters in length were dropped
            unless they are headwaters or connect to upstream segments already
            marked as habitat.
          </li>
          <li>
            We manually selected NHD flowlines that were not otherwise selected
            above if they had a suitable amount of visual overlap and landscape
            position suggested that habitat could be extended to their entire
            lengths. We manually deselected NHD flowlines that were erroneously
            marked as habitat above due to spatial proximity; these include
            canals / ditches that closely parallel waterways with habitat.
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the Lahontan cutthroat trout habitat data, attributed
          at the entire NHDPlusHR flowline level; it does not include elevation
          gradients or other natural barriers that may have been included within
          the original data.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="CoastalCutthroatTrout" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Coastal Cutthroat Trout Habitat (California)
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            <Paragraph>
              Coastal cutthroat trout habitat data in California were derived
              from habitat linework provided by the Pacific States Marine
              Fisheries Commission. Because coastal cutthroat trout habitat data
              are already prepared for Oregon and Washington using StreamNet
              data (above), this additional data was limited to California.
            </Paragraph>
          </Box>

          <Box>
            <GatsbyImage
              image={coastalCutthroatTroutImage}
              alt="Cutthroat Trout"
            />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Cutthroat Trout |{' '}
              <OutboundLink to="https://www.fws.gov/media/releasing-cutthroat">
                U.S. Fish and Wildlife Service
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the coastal cutthroat trout
          habitat data to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>Selected habitat linework within NHD region 18.</li>
          <li>
            Selected NHDPlusHR flowlines that intersected a 100 meter buffer
            around the habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches or network loops. The
            remaining flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 100 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 65%
            of its length is within the buffer and the total amount of overlap
            is less than 1 kilometer different from its total length. Any Any
            fragments that have high overlap with the buffer but are less than
            300 meters in length were dropped unless they are headwaters or
            connect to upstream segments already marked as habitat.
          </li>
          <li>
            The outputs of steps 4 and 5 are used to define anchor points in a
            network analysis to fill gaps between segments identified as
            habitat. We created a linear directed graph facing downstream using
            the NHDPlusHR network toplogy (excluding any network loops and
            canals / ditches) and traversed this graph from the anchor points to
            upstream points of disconnected habitat linework (gaps must be less
            than 100 flowlines long). We selected flowlines identified from
            traversing these networks to fill gaps if they did not bridge
            distinct habitat groups and had at least 10% overlap with a 200
            meter buffer around the habitat linework.
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the coastal cutthroat trout habitat data, attributed
          at the entire NHDPlusHR flowline level; it does not include elevation
          gradients or other natural barriers that may have been included within
          the original data.
        </Paragraph>
      </Box>

      <Divider />

      <Box id="ColoradoRiverCutthroatTrout" sx={{ mt: '3rem' }}>
        <Heading as="h2" variant="heading.section">
          Colorado River Cutthroat Trout Habitat
        </Heading>

        <Grid columns="2fr 1fr" gap={4}>
          <Box>
            Colorado River cutthroat trout habitat data were derived from data
            provided by the Colorado Cutthroat Trout Working Group.
          </Box>

          <Box>
            <GatsbyImage
              image={coloradoRiverCutthroatTroutImage}
              alt="Colorado River Cutthroat Trout"
            />
            <Text variant="help" sx={{ fontSize: 0 }}>
              Photo: Colorado River |{' '}
              <OutboundLink to="https://en.wikipedia.org/wiki/Colorado_River_cutthroat_trout#/media/File:Colo_river_cutthroat_BLM.jpg">
                Bureau of Land Management
              </OutboundLink>
            </Text>
          </Box>
        </Grid>

        <Paragraph sx={{ mt: '2rem', fontWeight: 'bold' }}>
          We used the following steps to attribute the Colorado River cutthroat
          trout habitat data to NHDPlusHR flowlines:
        </Paragraph>
        <Box
          as="ol"
          sx={{
            mt: '0.5rem',
          }}
        >
          <li>Reprojected to the USGS CONUS Albers projection.</li>
          <li>
            Selected NHDPlusHR flowlines that intersected a 50 meter buffer
            around the habitat linework for further processing below.
          </li>
          <li>
            Selected any flowlines where both the upstream and downstream
            endpoints fall within 1 meter of habitat linework and marked them as
            habitat if they were not canals / ditches or network loops. The
            remaining flowlines are retained for further processing below.
          </li>
          <li>
            Calculated the amount of overlap with the 50 meter buffer around
            habitat linework, and marked a flowline as habitat if at least 50%
            of its length is within the buffer and the total amount of overlap
            is less than 1 kilometer different from its total length, or if its
            upstream endpoint is within 1 meter of the habitat linework and has
            at least 25% overlap. Any Any fragments that have high overlap with
            the buffer but are less than 150 meters in length were dropped
            unless they are headwaters or connect to upstream segments already
            marked as habitat.
          </li>
          <li>
            We also extracted any flowlines that had significant overlap with
            Colorado River cutthroat trout waterbodies identified as current
            populations (excluded waterbodies specifically marked as
            recreational populations or populations no longer present).
          </li>
          <li>
            We visually and quantitatively compared the extracted NHDPlusHR
            flowlines tagged as habitat to the original data to ensure
            reasonable spatial correspondence; the overall linework was similar
            and had roughly similar lengths.
          </li>
        </Box>
        <Paragraph variant="help" sx={{ mt: '2rem' }}>
          Note: the habitat data included used within this tool is a best first
          approximation of the Colorado River cutthroat trout habitat data,
          attributed at the entire NHDPlusHR flowline level; it does not include
          elevation gradients or other natural barriers that may have been
          included within the original data.
        </Paragraph>
      </Box>
    </Container>
  </Layout>
)

HabitatMethodsPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    pnwSalmonImage: PropTypes.object.isRequired,
    pswSalmonImage: PropTypes.object.isRequired,
    brookTroutImage: PropTypes.object.isRequired,
    brookTroutImage2: PropTypes.object.isRequired,
    sturgeonImage: PropTypes.object.isRequired,
    apacheTroutImage: PropTypes.object.isRequired,
    coastalCutthroatTroutImage: PropTypes.object.isRequired,
    coloradoRiverCutthroatTroutImage: PropTypes.object.isRequired,
    lahontanCutthroatTroutImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NetworkHabitatMethodsPageQuery {
    headerImage: file(
      relativePath: { eq: "brandon-enPHTN3OPRw-unsplash.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    pnwSalmonImage: file(relativePath: { eq: "52633917843_8c189a8ea2_c.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    pswSalmonImage: file(relativePath: { eq: "52706030122_dc2b358ec0_c.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    brookTroutImage: file(relativePath: { eq: "4752172480_74c20f37af_c.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    brookTroutImage2: file(
      relativePath: { eq: "8574372559_f05ce9e42a_c.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    sturgeonImage: file(relativePath: { eq: "6359207695_1d41348492_c.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    apacheTroutImage: file(relativePath: { eq: "usfws-apache-trout.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    coastalCutthroatTroutImage: file(
      relativePath: { eq: "usfws-releasing-cutthroat.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    coloradoRiverCutthroatTroutImage: file(
      relativePath: { eq: "Colo_river_cutthroat_BLM.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    lahontanCutthroatTroutImage: file(
      relativePath: { eq: "usfws-lahontan-cutthroat-trout.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 400
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
  }
`

export default HabitatMethodsPage

export const Head = () => <SEO title="Aquatic Species Habitat Methods" />
