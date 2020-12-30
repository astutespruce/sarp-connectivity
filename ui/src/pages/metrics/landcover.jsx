import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import { OutboundLink } from 'components/Link'
import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { Columns } from 'components/Grid'
import HighlightBox from 'components/Layout/HighlightBox'
import {
  PageTitle,
  PageContainer,
  Section,
  Title,
  Column,
  LargeText,
} from 'content/styles'

const LandcoverPage = ({ data: { headerImage } }) => (
  <Layout title="Floodplain Natural Landcover">
    <HeaderImage
      image={headerImage.childImageSharp.fluid}
      height="20vh"
      minHeight="18rem"
      position="center"
      credits={{
        author:
          'Loakfoma Creek, Noxubee National Wildlife Refuge, Mississippi. U.S. Fish and Wildlife Service.',
        url:
          'https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/',
      }}
    />

    <PageContainer>
      <PageTitle>Floodplain natural landcover</PageTitle>
      <LargeText>
        Rivers and streams that have a greater amount of natural landcover in
        their floodplain are more likely to have higher quality aquatic habitat.
        These areas may have more cool-water refugia for temperature sensitive
        species due to shading from the overstory, and may have fewer water
        quality issues. In contrast, rivers that have less natural landcover are
        more likely to be altered and have impaired water quality.
      </LargeText>

      <Section>
        <Columns>
          <Column>
            <HighlightBox
              icon="nat_landcover_low"
              title="Low natural landcover"
            >
              <p>
                Barriers with less natural landcover are less likely to
                contribute high quality habitat for aquatic species if removed.
              </p>
            </HighlightBox>
          </Column>
          <Column>
            <HighlightBox
              icon="nat_landcover_high"
              title="High natural landcover"
            >
              <p>
                Barriers with aquatic networks that have more natural landcover
                are more likely to contribute higher quality habitat if they are
                removed.
              </p>
            </HighlightBox>
          </Column>
        </Columns>
      </Section>

      <Section>
        <Title>Methods:</Title>
        <ol>
          <li>
            Floodplains are delineated using data derived from FATHOM Inc, which
            has modeled 30 by 30 meter 100 year floodplain boundaries. For more
            information visit:
            <br />
            <OutboundLink
              from="/metrics/landcover"
              to="https://iopscience.iop.org/article/10.1088/1748-9326/aaac65/pdf"
            >
              https://iopscience.iop.org/article/10.1088/1748-9326/aaac65/pdf
            </OutboundLink>
          </li>
          <li>
            Natural landcover is derived from the USDA National Landcover
            Database (NLCD) 2016 30 by 30 meter landcover raster dataset. For
            more information see:{' '}
            <OutboundLink
              from="/metrics/landcover"
              to="https://www.mrlc.gov/data/nlcd-2016-land-cover-conus"
            >
              https://www.mrlc.gov/data/nlcd-2016-land-cover-conus
            </OutboundLink>
            .
          </li>
          <li>
            Natural landcover is extracted from the overall NLCD dataset and
            clipped to the floodplain area for analysis.
          </li>
          <li>
            The contributing watershed (catchment) of each stream and river
            reach is extracted from the NHDPlus dataset.
          </li>
          <li>
            The total amount of natural landcover within the catchment area as
            well as the floodplain area of that catchment area are tallied for
            each functional network.
          </li>
          <li>
            Floodplain natural landcover is measured from the overall percent of
            natural landcover throughout the entire functional network.
          </li>
        </ol>
      </Section>
    </PageContainer>
  </Layout>
)

LandcoverPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query NaturalLandcoverQuery {
    headerImage: file(relativePath: { eq: "6882770647_c43a945282_o.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200, quality: 90) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
  }
`

export default LandcoverPage
