import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import {
  Box,
  Flex,
  Container,
  Divider,
  Grid,
  Heading,
  Paragraph,
  Text,
} from 'theme-ui'

import { useSummaryData } from 'components/Data'
import { StateDownloadTable } from 'components/Download'
import { Layout, SEO } from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { RegionActionLinks, RegionStats } from 'components/Regions'
import { REGIONS } from 'config'
import { formatNumber } from 'util/format'

const regionID = 'ak'
const {
  [regionID]: { name, states, inDevelopment },
} = REGIONS

const AlaskaRegionPage = ({
  data: {
    headerImage: {
      childImageSharp: { gatsbyImageData: headerImage },
    },
    map: {
      childImageSharp: { gatsbyImageData: map },
    },
  },
}) => {
  const { [regionID]: summary } = useSummaryData()

  return (
    <Layout>
      <HeaderImage
        image={headerImage}
        height="20vh"
        minHeight="18rem"
        credits={{
          author: 'Zetong Li',
          url: 'https://unsplash.com/photos/UC1HP-zhEmU',
        }}
      />

      <Container>
        <Flex
          sx={{
            alignItems: 'baseline',
            justifyContent: 'space-between',
            borderBottom: '1px solid',
            borderBottomColor: 'grey.2',
            pb: '0.25rem',
          }}
        >
          <Heading as="h1" sx={{ flex: '1 1 auto' }}>
            {name} Region
          </Heading>
          {inDevelopment ? (
            <Text sx={{ flex: '0 0 auto', fontSize: 2, color: 'grey.8' }}>
              (in development)
            </Text>
          ) : null}
        </Flex>
        <Grid columns={2} gap={5} sx={{ mt: '2rem' }}>
          <Box>
            <Box sx={{ border: '1px solid', borderColor: 'grey.4' }}>
              <GatsbyImage
                image={map}
                alt={`${name} region map`}
                sx={{ border: '1px solid', borderColor: 'grey.3' }}
              />
            </Box>
            <Text sx={{ fontSize: 1, color: 'grey.7' }}>
              Map of {formatNumber(summary.dams)} inventoried dams and{' '}
              {formatNumber(summary.smallBarriers)} road-related barriers likely
              to impact aquatic organisms in the {name}
              region.
            </Text>
          </Box>
          <Box>
            <Heading as="h4" sx={{ mb: '1rem' }}>
              Includes {states.length} states with:
            </Heading>

            <RegionStats {...summary} />
          </Box>
        </Grid>
        <RegionActionLinks region={regionID} />

        {/* TODO: data sources section */}

        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            Statistics by state:
          </Heading>
          <Box sx={{ mt: '0.5rem' }}>
            <StateDownloadTable region={regionID} {...summary} />
          </Box>
        </Box>
        <Divider sx={{ my: '4rem' }} />
        <Box variant="boxes.section">
          <Heading as="h2" variant="heading.section">
            You can help!
          </Heading>
          <Paragraph sx={{ mt: '1rem' }}>
            You can help improve the inventory You can help improve the
            inventory by sharing data, assisting with field reconnaissance to
            evaluate the impact of aquatic barriers, or even by reporting issues
            with the inventory data in this tool.
            <br />
            <br />
            <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
            more about how you can help improve aquatic connectivity in the
            {name} region.
          </Paragraph>
        </Box>
      </Container>
    </Layout>
  )
}

AlaskaRegionPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
    map: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query AlaskaRegionPageQuery {
    headerImage: file(
      relativePath: { eq: "zetong-li-UC1HP-zhEmU-unsplash.jpg" }
    ) {
      childImageSharp {
        gatsbyImageData(
          layout: FULL_WIDTH
          formats: [AUTO, WEBP]
          placeholder: BLURRED
        )
      }
    }
    map: file(relativePath: { eq: "maps/ak.png" }) {
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

export default AlaskaRegionPage

export const Head = () => <SEO title={`${name} Region`} />
