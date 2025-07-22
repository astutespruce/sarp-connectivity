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

const EPAMethodsPage = ({ data: { headerImage } }) => (
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
      <Heading as="h1">
        Joining EPA water quality assessment to NHD High Resolution Flowlines
      </Heading>
      <Paragraph variant="paragraph.large" sx={{ mt: '2rem' }}>
        Selected areas and lines from the{' '}
        <OutboundLink to="https://www.epa.gov/waterdata/waters-geospatial-data-downloads#NationalGeospatialDatasets">
          EPA ATTAINS water quality assessment
        </OutboundLink>{' '}
        were joined to NHD High Resolution flowlines for use in this tool. We
        extracted areas and lines from the EPA water quality assesment where one
        or more of the following were listed as causal factors:
      </Paragraph>
      <Box as="ul">
        <li>temperature</li>
        <li>impaired biota (cause unknown)</li>
        <li>oxygen depletion</li>
        <li>algal growth</li>
        <li>flow alterations</li>
        <li>habitat alterations</li>
        <li>hydrologic alteration</li>
        <li>fish kills (cause unknown)</li>
      </Box>

      <Paragraph>
        We used the following methods to join EPA water quality assessment data
        to flowlines:
      </Paragraph>
      <Box as="ul">
        <li>
          Extracted EPA areas and lines that have at least one of the causes
          above present, and reprojected to USGS CONUS Albers. Removed any EPA
          lines within EPA areas; these were typically redundant, and the
          methods below assign flowlines based on overlap with the areas.
        </li>
        <li>
          Attempted to identify lines that represent the outer boundaries of
          waterbodies (incorrect representation in source dataset); these were
          especially common in Oklahoma and somewhat common in California. For
          any line where the first point intersected the last point in Oklahoma
          or California, this converted those into polygon areas instead of
          lines.
          <br />
          <br />
          Note: not all areas could be correctly extracted this way. There were
          multiple instances where the EPA line did not form a self-closing ring
          (e.g., if the waterbody was represented using multiple lines instead
          of a single ring), or the EPA lines represented parts but not all of
          the shoreline of a given waterbody.
        </li>
        <li>
          All NHD flowlines that were at least 75% contained within an EPA area
          were assigned to that area. Where a flowline was assigned to multiple
          areas, the area with the highest amount of overlap and smallest size
          was retained.
        </li>
        <li>
          EPA lines were buffered based on a tolerance determined through manual
          review of EPA lines versus NHD flowlines in each NHD region (HUC2).
          This tolerance ranged from 50 meters (default) to 150 meters in areas
          where there was very poor alignment between the EPA lines and the
          corresponding NHD flowlines.
        </li>
        <li>
          All NHD flowlines that intersect with EPA lines were initially tagged
          to those EPA lines. These combinations were kept if one of the
          following was true:
          <ul>
            <li>
              there was at least 75% overlap between the NHD flowline and the
              buffer around the EPA line
            </li>
            <li>
              the upstream and downstream endpoints of the NHD flowline were
              both within 5 meters of the EPA line and had at least 50% overlap
              with the buffer around the EPA line
            </li>
            <li>
              the NHD flowline was associated with multiple EPA lines and had at
              least 25% overlap
            </li>
            <li>
              the NHD flowline was identified via manual review as being most
              likely associated with an EPA line, but not otherwise detected
              based on the rules above
            </li>
          </ul>
        </li>
        <li>
          Where an NHD flowline was associated with multiple EPA lines, the
          combination with the highest overlap and smallest Hausdorff distance
          between the flowline and EPA line was retained. This metric
          approximates the combination with the best fit when both represent
          similar lines; it does not work when the EPA line or flowline are
          substantially different lengths.
          <br />
          <br />
          Note: there are likely cases where it is valid to retain multiple EPA
          lines per NHD flowline. However, most cases that we manually reviewed
          of an NHD flowline having multiple associated EPA lines were the
          result of overlapping buffers rather than best fit to the underlying
          EPA line.
        </li>
      </Box>

      <Paragraph variant="help">
        <b>Important:</b>
        <br />
        These methods associate the EPA assessment data with flowlines, which
        includes errors of omission and comission when matching to NHD
        flowlines. EPA assessment data were joined to whole flowlines, whereas
        the underlying assessment may be based on a shorter stream reach, such
        as those subdivided by barriers in the aquatic network or other
        landscape contextual factors. Thus the associated flowlines may extend
        somewhat beyond the specific reaches for which water quality issues were
        recorded by EPA. Furthermore, the linework representing certain larger
        rivers and braided channels in the EPA data had very poor alignment with
        NHD flowlines, possibly due to old versions of the hydrology used in the
        EPA dataset which no longer reflects the position of the river channel.
        This means that some of these lines within the EPA data could not be
        attributed to NHD flowlines.
        <br />
        <br />
        These flowline assignments have not been reviewed or approved by EPA and
        should be treated as reasonable approximations only.
      </Paragraph>
    </Container>
  </Layout>
)

EPAMethodsPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
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
  }
`

export default EPAMethodsPage

export const Head = () => <SEO title="Aquatic Species Habitat Methods" />
