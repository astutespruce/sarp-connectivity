import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { Box, Container, Flex, Grid, Image, Paragraph, Heading } from 'theme-ui'

import { Layout, HighlightBox } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Link, OutboundLink } from 'components/Link'
import NetworkGraphicSVG from 'images/functional_network.svg'

const ScoringMethodsPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    damPhoto: {
      childImageSharp: { gatsbyImageData: damPhoto },
    },
  },
}) => (
  <Layout title="Prioritizing aquatic barriers for removal">
    <HeaderImage
      image={headerImage}
      height="30vh"
      minHeight="18rem"
      credits={{
        author:
          'Steeles Mill Dam Hitchcock Creek during removal. Peter Raabe, American Rivers.',
      }}
    />

    <Container>
      <Heading as="h1">Prioritizing aquatic barriers for removal</Heading>
      <Flex sx={{ alignItems: 'center', mt: '3rem' }}>
        <Box variant="boxes.step">1</Box>
        <Heading as="h3" sx={{ flex: '1 1 auto', fontWeight: 'normal' }}>
          Aquatic barriers are identified and measured for their potential
          impact on aquatic organisms:
        </Heading>
      </Flex>
      <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '2rem' }}>
        <Box>
          <Paragraph>
            Aquatic barriers are natural and human-made structures that impede
            the passage of aquatic organisms through the river network.
            <br />
            <br />
            They include:
          </Paragraph>
          <Box as="ul">
            <li>Waterfalls</li>
            <li>Dams</li>
            <li>Road-related barriers</li>
          </Box>
          <Paragraph sx={{ mt: '1rem' }}>
            Where possible, human-made barriers have been assessed using field
            reconnaissance to determine their likely impact on aquatic organisms
            as well as their feasibility of removal. You can leverage these
            characteristics to select a smaller number of barriers to
            prioritize.
          </Paragraph>
        </Box>
        <Box>
          <GatsbyImage image={damPhoto} alt="Hartwell Dam" />
          <Box sx={{ fontSize: 0 }}>
            <OutboundLink to="https://www.flickr.com/photos/savannahcorps/9272554306/">
              Hartwell Dam, Georgia. Billy Birdwell, U.S. Army Corps of
              Engineers.
            </OutboundLink>
          </Box>
        </Box>
      </Grid>

      <Box variant="boxes.section">
        <Flex sx={{ alignItems: 'center' }}>
          <Box variant="boxes.step">2</Box>
          <Heading as="h3" sx={{ flex: '1 1 auto', fontWeight: 'normal' }}>
            Aquatic barriers are measured for their impact on the aquatic
            network:
          </Heading>
        </Flex>

        <Grid columns={[0, '5fr 3fr']} gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Paragraph>
              Functional aquatic networks are the stream and river reaches that
              extend upstream from a barrier or river mouth to either the origin
              of that stream or the next upstream barrier. They form the basis
              for the aquatic network metrics used in this tool.
              <br />
              <br />
              To calculate functional networks, all barriers were snapped to
              the&nbsp;
              <OutboundLink to="https://www.usgs.gov/core-science-systems/ngp/national-hydrography/nhdplus-high-resolution">
                USGS High Resolution National Hydrography Dataset
              </OutboundLink>
              &nbsp;(NHDPlus). Where possible, their locations were manually
              inspected to verify their correct position on the aquatic network.
              <br />
              <br />
              <Link to="/network_methods">
                Read more about network analysis methods
              </Link>
              .
            </Paragraph>

            <Flex sx={{ alignItems: 'flex-start', mt: '2rem' }}>
              <Box sx={{ flex: '0 0 auto', color: 'highlight', mr: '1rem' }}>
                <ExclamationTriangle size="1.5rem" />
              </Box>
              <Paragraph variant="help" sx={{ flex: '1 1 auto' }}>
                Note: due to limitations of existing data sources for aquatic
                networks, not all aquatic barriers can be correctly located on
                the aquatic networks. These barriers are not included in the
                network connectivity analysis and cannot be prioritized using
                this tool. However, these data can still be downloaded from this
                tool and used for offline analysis.
              </Paragraph>
            </Flex>
          </Box>

          <Box display={['none', 'unset']}>
            <Image src={NetworkGraphicSVG} sx={{ height: '29rem' }} />
          </Box>
        </Grid>
      </Box>

      <Box variant="boxes.section">
        <Flex sx={{ alignItems: 'center' }}>
          <Box variant="boxes.step">3</Box>
          <Heading as="h3" sx={{ fontWeight: 'normal' }}>
            Barriers are characterized using metrics that describe the quality
            and status of their functional networks:
          </Heading>
        </Flex>

        <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
          <HighlightBox icon="length_high" title="Network Length">
            <Paragraph>
              Network length measures the amount of connected aquatic network
              length that would be added to the network by removing the barrier.
              Longer connected networks may provide more overall aquatic habitat
              for a wider variety of organisms and better support dispersal and
              migration.
              <br />
              <br />
              <Link to="/metrics/length">Read more...</Link>
            </Paragraph>
          </HighlightBox>

          <HighlightBox icon="size_classes_high" title="Network Complexity">
            <Paragraph>
              Network complexity measures the number of unique upstream size
              classes that would be added to the network by removing the
              barrier. A barrier that has upstream tributaries of different size
              classes, such as small streams, small rivers, and large rivers,
              would contribute a more complex connected aquatic network if it
              was removed.
              <br />
              <Link to="/metrics/complexity">Read more...</Link>
            </Paragraph>
          </HighlightBox>

          <HighlightBox icon="sinuosity_high" title="Channel Alteration">
            <Paragraph>
              Altered river and stream reaches are those that are specifically
              identified as canals or ditches. These represent areas where the
              hydrography, flow, and water quality may be highly altered
              compared to natural conditions.
              <br />
              <Link to="/metrics/unaltered">Read more...</Link>
            </Paragraph>
          </HighlightBox>

          <HighlightBox icon="nat_landcover_high" title="Natural Landcover">
            <Paragraph>
              Natural landcover measures the amount of area within the
              floodplain of the upstream aquatic network that is in natural
              landcover. Rivers and streams that have a greater amount of
              natural landcover in their floodplain are more likely to have
              higher quality aquatic habitat.
              <br />
              <Link to="/metrics/landcover">Read more...</Link>
            </Paragraph>
          </HighlightBox>
        </Grid>
      </Box>

      <Box variant="boxes.section">
        <Flex sx={{ alignItems: 'center' }}>
          <Box variant="boxes.step">4</Box>
          <Heading as="h3" sx={{ flex: '1 1 auto', fontWeight: 'normal' }}>
            Metrics are combined and ranked to create three scenarios for
            prioritizing barriers for removal:
          </Heading>
        </Flex>
        <Grid columns={[0, 2]} gap={4} sx={{ mt: '2rem' }}>
          <HighlightBox title="Network Connectivity">
            <Paragraph>
              Aquatic barriers prioritized according to network connectivity are
              driven exclusively on the total amount of functional aquatic
              network that would be reconnected if a given dam was removed. This
              is driven by the&nbsp;
              <Link to="/metrics/length">network length</Link> metric. No
              consideration is given to other characteristics that measure the
              quality and condition of those networks.
            </Paragraph>
          </HighlightBox>

          <HighlightBox title="Watershed Condition">
            <Paragraph>
              Aquatic barriers prioritized according to watershed condition are
              driven by metrics related to the overall quality of the aquatic
              network that would be reconnected if a given dam was removed. It
              is based on a combination of&nbsp;
              <Link to="/metrics/complexity">network complexity</Link>
              ,&nbsp;
              <Link to="/metrics/unaltered">percent unaltered</Link>, and&nbsp;
              <Link to="/metrics/landcover">floodplain natural landcover</Link>.
              Each of these metrics is weighted equally.
            </Paragraph>
          </HighlightBox>
        </Grid>

        <HighlightBox
          title="Network Connectivity + Watershed Condition"
          mt="2rem"
        >
          <Paragraph>
            Aquatic barriers prioritized according to combined network
            connectivity and watershed condition are driven by both the length
            and quality of the aquatic networks that would be reconnected if
            these barriers are removed. <b>Network connectivity</b> and{' '}
            <b>watershed condition</b> are weighted equally.
          </Paragraph>
        </HighlightBox>
      </Box>

      <Box variant="boxes.section">
        <Paragraph>
          To reduce the impact of outliers, such as very long functional
          networks, barriers are scored based on their relative rank within the
          overall range of unique values for a given metric. Many barriers have
          the same value for a given metric and are given the same relative
          score; this causes the distribution of values among scores to be
          highly uneven in certain areas.
          <br />
          <br />
          Once barriers have been scored for each of the above scenarios, they
          are binned into 20 tiers to simplify interpretation and use. To do
          this, barriers that fall in the best 5% of the range of scores for
          that metric are assigned to Tier 1 (top tier), whereas barriers that
          fall in the worst 5% of the range of scores for that metric are
          assigned Tier 20 (bottom tier).
          <br />
          <br />
        </Paragraph>

        <Flex sx={{ alignItems: 'flex-start', mt: '2rem' }}>
          <Box sx={{ flex: '0 0 auto', color: 'highlight', mr: '1rem' }}>
            <ExclamationTriangle size="1.5rem" />
          </Box>
          <Paragraph variant="help" sx={{ flex: '1 1 auto' }}>
            Note: tiers are based on position within the range of observed
            scores for a given area. They are <i>not</i> based on the frequency
            of scores, such as percentiles, and therefore may have a highly
            uneven number of barriers per tier depending on the area. In
            general, there are fewer barriers in the top tiers than there are in
            the bottom tiers. This is largely because many barriers share the
            same value for a given metric.
          </Paragraph>
        </Flex>
      </Box>
    </Container>
  </Layout>
)

ScoringMethodsPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    damPhoto: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query ScoringMethodsPageQuery {
    headerImage: file(
      relativePath: {
        eq: "Steeles_Mill_Dam_Hitchcock_Creek_during_removal__Peter_Raabe_A.jpg"
      }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    damPhoto: file(relativePath: { eq: "9272554306_b34bf886f4_z.jpg" }) {
      childImageSharp {
        gatsbyImageData(
          layout: CONSTRAINED
          width: 640
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
  }
`

export default ScoringMethodsPage
