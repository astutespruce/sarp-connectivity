import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import Img from 'gatsby-image'
import { FaChartBar, FaSearchLocation } from 'react-icons/fa'

import { Text } from 'components/Text'
import { Link } from 'components/Link'
import { SecondaryButton as Button } from 'components/Button'
import { Columns, Flex } from 'components/Grid'
import styled, { themeGet } from 'style'

import { Section, Title, NarrowColumn, WideColumn } from '../styles'

const Header = styled(Flex).attrs({ alignItems: 'center' })`
  font-size: 2rem;
  margin-bottom: 1rem;
  color: ${themeGet('colors.grey.900')};
`

const Subtitle = styled(Text)`
  margin-left: 0.25em;
`

const BarIcon = styled(FaChartBar)`
  width: 1em;
  height: 1em;
`

const SearchIcon = styled(FaSearchLocation)`
  width: 1em;
  height: 1em;
`

const Tool = () => {
  const {
    prioritize: {
      childImageSharp: { fluid: prioritizeImage },
    },
    summarize: {
      childImageSharp: { fluid: summarizeImage },
    },
  } = useStaticQuery(graphql`
    query {
      prioritize: file(relativePath: { eq: "prioritize.jpg" }) {
        childImageSharp {
          fluid(maxWidth: 640, quality: 100) {
            ...GatsbyImageSharpFluid_withWebp
          }
        }
      }
      summarize: file(relativePath: { eq: "summarize.jpg" }) {
        childImageSharp {
          fluid(maxWidth: 640, quality: 100) {
            ...GatsbyImageSharpFluid_withWebp
          }
        }
      }
    }
  `)

  return (
    <Section>
      <Title>
        The Southeast Aquatic Barrier Prioritization Tool empowers you with the
        latest inventory data:
      </Title>
      <Header>
        <BarIcon />
        <Subtitle>Summarize the inventory across the region</Subtitle>
      </Header>
      <Columns>
        <WideColumn>
          <p>
            Explore summaries of the inventory across the region by state,
            county, or different levels of watersheds and ecoregions.
            <br />
            <br />
            These summaries are a good way to become familiar with the level of
            aquatic fragmentation across the Southeast. Find out how many
            aquatic barriers have already been inventoried in your area! Just
            remember, the inventory is a living database, and is not yet
            comprehensive across the region.
            <br />
            <br />
            <Link to="/summary">
              <Button>
                <BarIcon />
                &nbsp; Start summarizing
              </Button>
            </Link>
          </p>
        </WideColumn>
        <NarrowColumn>
          <Link to="/summary">
            <Img fluid={summarizeImage} alt="Summarize View" />
          </Link>
        </NarrowColumn>
      </Columns>

      <br />
      <br />

      <Header>
        <SearchIcon />
        <Subtitle>Prioritize aquatic barriers for removal</Subtitle>
      </Header>
      <Columns>
        <WideColumn>
          <p>
            Identify barriers for further investigation based on the criteria
            that matter to you.
            <br />
            <br />
            You can select specific geographic areas for prioritization,
            including counties, states, watersheds, and ecoregions. You can
            filter the available barriers based on criteria such as likely
            feasibility for removal, height, and more. Once you have prioritized
            aquatic barriers, you can download a CSV file for further analysis.
            <br />
            <br />
            <Link to="/priority">
              <Button>
                <SearchIcon />
                &nbsp; Start prioritizing
              </Button>
            </Link>
          </p>
        </WideColumn>
        <NarrowColumn>
          <Link to="/priority">
            <Img fluid={prioritizeImage} alt="Priority View" />
          </Link>
        </NarrowColumn>
      </Columns>
    </Section>
  )
}

export default Tool
