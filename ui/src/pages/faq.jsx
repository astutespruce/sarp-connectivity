import React from 'react'
import PropTypes from 'prop-types'
import { Box, Container, Heading, Paragraph, Text } from 'theme-ui'
import { graphql } from 'gatsby'

import { MAP_SERVICES, siteMetadata } from 'config'
import { Layout, SEO } from 'components/Layout'
import { Link, OutboundLink } from 'components/Link'
import { HeaderImage } from 'components/Image'

const { date, version } = siteMetadata

const FAQPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.gatsbyImageData}
      title="Frequently asked questions"
      height="20vh"
      minHeight="18rem"
      credits={{
        author: 'Kazuend',
        url: 'https://unsplash.com/photos/cCthPLHmrzI',
      }}
    />
    <Container
      sx={{
        pb: '4rem',
        '& h2': { mb: '0.5rem' },
        '& > div + div': { mt: '3rem' },
      }}
    >
      <Box>
        <Heading as="h2">
          What is the purpose of this Inventory and Prioritization Tool?
        </Heading>
        <Paragraph>
          The objective of this inventory and tool is to build a community of
          practice among resource managers and enable them to identify high
          priority aquatic connectivity restoration projects. Regularly updating
          barriers in this inventory allows it to better reflect the degree of
          aquatic habitat fragmentation from aquatic barriers across political
          boundaries at a national scale. We provide a collaborative atmosphere
          where all resource managers can contribute to the collective effort of
          restoring rivers and streams through aquatic barrier removal.
          <br />
          <br />
          You can help improve the inventory by sharing data, assisting with
          field reconnaissance to evaluate the impact of aquatic barriers,
          joining a Aquatic Connectivity Team, or even by reporting issues with
          the inventory data in this tool.
          <br />
          <br />
          <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
          more about how you can help improve this barrier inventory and tool.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">
          What can the Inventory and Prioritization Tool do?
        </Heading>
        <Paragraph>
          The prioritization tool allows users to{' '}
          <Link to="/explore">explore and download barrier</Link> inventory
          information at different scales. It also allows users to{' '}
          <Link to="/priority">prioritize</Link> barriers at different scales
          using different filtering approaches and different prioritization
          scenarios. It is also possible to{' '}
          <Link to="/restoration">summarize accomplishments</Link> over multiple
          years, such as miles restored through barrier removal by year.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">
          What kind of barriers does the Inventory track?
        </Heading>
        <Paragraph>
          We track dams (including diversions, weirs, low head dams), assessed
          road stream crossings, and waterfalls. We do not track beaver dams or
          other non-structural barriers at this time, though it is possible that
          we may track other types of barriers in the future.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">
          What data sources are included in the Inventory?
        </Heading>
        <Paragraph>
          This inventory is compiled from multiple sources at multiple scales.
          To best leverage data sources that are regularly updated by their data
          providers within existing efforts, we update with the best available
          data from data providers approximately four times a year.
          <br />
          <br />
          For a list of datasets included in the inventory, please see{' '}
          <OutboundLink to="https://docs.google.com/document/d/1mUwk9rHukmY1D_NInxjdIxbBVfILD1Y8Xr-lMqjV4xU/edit?usp=sharing">
            this link
          </OutboundLink>
          . If you know of a data source we have not included, please fill out{' '}
          <OutboundLink to="https://forms.gle/5kWN3D56hSijLFrU6">
            this form
          </OutboundLink>{' '}
          and we will contact you to ensure that it is included.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">How is the Inventory maintained and updated?</Heading>
        <Paragraph>
          The objective of this inventory is to highlight the efforts of states
          and local partners by compiling information and readily updating it
          from living sources of truth on a regular basis. For efforts
          consistently maintained by partners, we have set up automatic scripts
          to extract data approximately four times a year and check for updates
          to incorporate into the National Inventory and Tool. For static
          efforts, data is incorporated into the inventory when identified. We
          readily work with our partners and technicians to edit data and
          identify new structures using aerial maps, as well as attribute social
          feasibility.
          <br />
          <br />
          If you are interested in helping to maintain our database and
          incorporate local relevance into its attributes using ArcGIS online,
          please{' '}
          <OutboundLink to="https://southeastaquatics.net/about/contact-us">
            contact us
          </OutboundLink>
          .
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">How do I cite the inventory?</Heading>
        <Paragraph>
          When downloading the data, you can find the citation within the Terms
          of Use text file. Alternatively, if citing the inventory in general,
          you may use the following citation:
          <Text sx={{ mt: '1rem', mx: '2rem', bg: 'grey.1', p: '1rem' }}>
            Southeast Aquatic Resources Partnership (SARP). 2024. Comprehensive
            Aquatic Barrier Inventory v{version} ({date}).{' '}
            <OutboundLink to="https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act">
              https://southeastaquatics.net/sarps-programs/aquatic-connectivity-program-act
            </OutboundLink>
            . (downloaded {new Date().toLocaleDateString()} from{' '}
            <OutboundLink to="https://aquaticbarriers.org">
              https://aquaticbarriers.org
            </OutboundLink>
            ). SARP/USFWS.
          </Text>
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">How can I report a missing barrier?</Heading>
        <Paragraph>
          Our inventory is the most comprehensive aquatic barrier inventory
          within the United States, but it is not perfect and is still lacking
          barriers, particularly low head dams and diversion structures. If you
          are exploring the tool and notice a missing barrier, please contact{' '}
          <a href="mailto:kat@southeastaquatics.net">
            kat@southeastaquatics.net
          </a>{' '}
          with the coordinates, or when prioritizing within the tool, scroll to
          the bottom of the sidebar for the barrier in question and click{' '}
          <b>Report a problem with this barrier</b>.
          <br />
          <br />
          The master inventory will likely be updated fairly quickly, but it may
          take several months for the public facing tool to reflect the new
          barrier. If you would like to know the priority of the new barrier, we
          can provide you with offline results via email.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">How are barriers prioritized within the Tool?</Heading>
        <Paragraph>
          Within the tool, a user can prioritize dams, assessed road stream
          crossings, or both barrier types together. Waterfalls are included
          within network analysis as well, but are not prioritized. A priority
          barrier to remove would be one that reconnects high quality habitat.
          For this reason, we calculate and use four metrics for each barrier:
        </Paragraph>
        <Box as="ul" sx={{ ml: '1rem', mt: '0.5rem', mb: '1.5rem' }}>
          <li>Miles restored by the potential removal of the structure</li>
          <li>
            Percent natural land cover within the floodplain of the
            structure&apos;s upstream network
          </li>
          <li>
            The percent of the upstream network that is altered by canals and
            ditching
          </li>
          <li>
            The complexity of the upstream network (number of stream size
            classes)
          </li>
        </Box>

        <Paragraph>
          These four metrics can be combined into three scenarios:
        </Paragraph>

        <Box as="ul" sx={{ ml: '1rem', mt: '0.5rem', mb: '1.5rem' }}>
          <li>network length</li>
          <li>watershed condition</li>
          <li>combined network lenght and watershed condition</li>
        </Box>

        <Paragraph>
          Within the prioritization tool, users can identify a targeted set of
          filters to prioritize based on a wide range of available filters.
          These filters include the number of threatened and endangered species
          in a HUC12, landowner type, environmental justice, number of barriers
          downstream to the ocean, and more. Once an output is generated, users
          can toggle between priorities for the area of interest and also
          explore results for perennial reaches only or all (perennial vs
          ephemeral/intermittent) reaches.
          <br />
          <br />
          Planned future enhancements include the ability to prioritize barriers
          for larger species vs smaller ones.
          <br />
          <br />
          More information about how barriers are prioritized can be found{' '}
          <Link to="/scoring_methods/">here</Link>.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">
          How does the Prioritization Tool deal with &quot;beneficial
          barriers&quot;?
        </Heading>
        <Paragraph>
          To incorporate local relevance into the inventory such as the presence
          of beneficial barriers which prevent the migration of invasive
          species, SARP works to code barriers within a Social Feasibility
          field. Barriers that may be invasive barriers are marked as such, and
          therefore not available for prioritization in the tool. However, this
          data is lacking, and unless this information is available within an
          existing inventory, we rely on our partners to tell us where these
          invasive barriers are located.
          <br />
          <br />
          To report an invasive species barrier miscoded within the inventory,
          as with missing barriers, please contact{' '}
          <a href="mailto:kat@southeastaquatics.net">
            kat@southeastaquatics.net
          </a>{' '}
          with the coordinates, or when prioritizing within the tool, scroll to
          the bottom of the sidebar for the barrier in question and click{' '}
          <b>Report a problem with this barrier</b>.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">
          How can I download barriers for a specific area?
        </Heading>
        <Paragraph>
          Use the{' '}
          <Link to="/explore">
            <b>Explore &amp; Download</b>
          </Link>{' '}
          page to select one or more states, counties, or hydrologic units for
          your area of interest. You can then download all dams, road-related
          barriers, or both types for that area.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">How can I download all available barriers?</Heading>
        <Paragraph>
          Use the download button on the bottom left of the{' '}
          <Link to="/explore">
            <b>Explore &amp; Download</b>
          </Link>{' '}
          page or the{' '}
          <Link to="/restoration">
            <b>Restoration</b>
          </Link>{' '}
          page to download all available dams and / or road-related barriers.
        </Paragraph>
      </Box>

      <Box>
        <Heading as="h2">
          How can I access map services to display barriers in a GIS
          application?
        </Heading>
        <Paragraph sx={{ mt: '0.5rem' }}>
          If you would like to access map services of a recent version of the
          aquatic barriers and connectivity results (may not match the exact
          version here), you can import one of the following connectivity
          analysis map services into your GIS tool of choice:
        </Paragraph>
        <Box as="ul" sx={{ mt: '0.5rem' }}>
          <li>
            <OutboundLink to={MAP_SERVICES.dams}>Dams</OutboundLink> based on
            networks that are cut by dams and waterfalls.
          </li>
          <li>
            <OutboundLink to={MAP_SERVICES.small_barriers}>
              Assessed road crossings
            </OutboundLink>{' '}
            based on networks that are cut by dams, waterfalls, and assessed
            crossings.
          </li>
          <li>
            <OutboundLink to={MAP_SERVICES.combined_barriers}>
              Dams and assessed road crossings
            </OutboundLink>{' '}
            based on networks that are cut by dams, waterfalls, and assessed
            crossings.
          </li>
        </Box>
      </Box>
    </Container>
  </Layout>
)

FAQPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query FAQPageQuery {
    headerImage: file(
      relativePath: { eq: "kazuend-cCthPLHmrzI-unsplash.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
  }
`

export default FAQPage

export const Head = () => <SEO title="Frequently asked questions" />
