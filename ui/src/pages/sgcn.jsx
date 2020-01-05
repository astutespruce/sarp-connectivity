import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'

import Layout from 'components/Layout'
import { HeaderImage } from 'components/Image'
import { OutboundLink } from 'components/Link'
import {
  PageTitle,
  PageContainer,
  Section,
  Title,
  Column,
  LargeText,
} from 'content/styles'

const LengthPage = ({ data: { headerImage } }) => (
  <Layout>
    <HeaderImage
      image={headerImage.childImageSharp.fluid}
      height="30vh"
      minHeight="18rem"
      position="center"
      credits={{
        author: 'U.S. Fish & Wildlife Service Southeast Region',
        url: 'https://www.flickr.com/photos/usfwssoutheast/33643109826/',
      }}
    />

    <PageContainer>
      <PageTitle>
        Listed Species and Species of Greatest Conservation Need
      </PageTitle>
      <LargeText>
        The presence of federally-listed threatened and endangered aquatic
        species and state and regionally-listed aquatic Species of Greatest
        Conservation Need is an important factor in evaluating the priority of a
        given barrier for removal or mitigation.
        <br />
        <br />
        We compiled information on the location of these species using element
        occurrence data obtained from state natural heritage programs or similar
        organizations. These data were limited to aquatic species, specifically
        fishes, crayfishes, mussels, snails, and amphibians
        <br />
        <br />
        We categorized species as follows:
        <ul>
          <li>
            Federally-listed species were identified based on data managed by
            the state programs or based on species lists from the U.S. Fish and
            Wildlife Service.
          </li>
          <li>
            State-listed Species of Greatest Conservation Need were identified
            using species lists from{' '}
            <OutboundLink to="https://www1.usgs.gov/csas/swap/">
              State Wildlife Action Plan species lists
            </OutboundLink>{' '}
            compiled by the U.S. Geological Survey.
          </li>
          <li>
            Regionally-listed Species of Greatest Conservation Need were
            identified using a species list from the Southeast Association of
            Fish and Wildlife Agencies.
          </li>
        </ul>
        <br />
        <br />
        <Title>
          Watersheds with most Species of Greatest Conservation Need{' '}
        </Title>
        We identified the top 10 watersheds for each state based on the number
        of state-listed species of Greatest Conservation Need aggregated up to
        the watershed (HUC8) level.
        <br />
        <br />
        <br />
        <Title>Caveats:</Title>
        <ul>
          <li>
            The presence of one or more of these species in the same
            subwatershed as a barrier does not necessarily mean that the species
            is directly impacted by that barrier. Likewise, it does not
            necessarily imply that the species will directly benefit by removal
            or mitigation of the barrier.
          </li>
          <li>
            Information on these species is limited and comprehensive
            information has not been provided for all states at this time.
          </li>
          <li>
            Due to variations in taxonomic representation of a given species or
            subspecies, not all species are necessarily correctly categorized
            according to the above breakdown.
          </li>
        </ul>
        {/* <br />
        <br />
        <ul>
          <li>
            TNC critical watersheds (critical watersheds for conservation of
            imperiled fish and mussels)
          </li>
          <li>
            TNC Hotspots (subbasins that contain 10 or more at-risk freshwater
            and mussel species)
          </li>
          <li>
            Watersheds with U.S. Fish and Wildlife Service Critical Habitat
            designations
          </li>
          <li>
            Southeast Aquatic Resources Partnership (SARP) priority watersheds
            (watersheds identified by SARP as key in preserving biodiversity in
            the southern U.S.)
          </li>
          <li>Watersheds containing aquatic passage inventories</li>
          <li>
            EPA priority watersheds (watersheds where the EPA and state partners
            agreed to focus to protect and restore waters)
          </li>
        </ul>
        <br />
        These watersheds were identified at the subbasin (HUC8) level.
        <br />
        <br />
        <a
          href={withPrefix('USFS_R8_priority_watersheds_2010.pdf')}
          download="USFS_R8_priority_watersheds_2010.pdf"
        >
          Download report.
        </a> */}
      </LargeText>
    </PageContainer>
  </Layout>
)

LengthPage.propTypes = {
  data: PropTypes.shape({
    headerImage: PropTypes.object.isRequired,
  }).isRequired,
}

export const pageQuery = graphql`
  query SGCNPageQuery {
    headerImage: file(relativePath: { eq: "33643109826_51296358b0_k.jpg" }) {
      childImageSharp {
        fluid(maxWidth: 3200) {
          ...GatsbyImageSharpFluid_withWebp
        }
      }
    }
  }
`

export default LengthPage
