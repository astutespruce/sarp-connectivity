import React from 'react'
import { graphql, useStaticQuery } from 'gatsby'
import { GatsbyImage } from 'gatsby-plugin-image'
import { Image } from 'rebass/styled-components'

import { Text } from 'components/Text'
import { Link, OutboundLink } from 'components/Link'
import { Columns } from 'components/Grid'
import styled from 'style'
import SARPLogoImage from 'images/sarp_logo.png'

import {
  Section,
  Title,
  NarrowColumn,
  WideColumn,
  ImageCredits,
} from '../styles'

const SARPLogo = styled(Image).attrs({ src: SARPLogoImage, width: '100%' })`
  max-width: 300px;
`

const MinorTitle = styled(Text).attrs({ as: 'h3', m: 0 })`
  font-weight: normal;
  font-size: 1.75rem;
`

const SARP = () => {
  const {
    forestStreamPhoto: {
      childImageSharp: { gatsbyImageData: forestStreamPhoto },
    },
    gaTeamPhoto: {
      childImageSharp: { gatsbyImageData: gaTeamPhoto },
    },
  } = useStaticQuery(graphql`
    query {
      forestStreamPhoto: file(
        relativePath: { eq: "6882770647_60c0d68a9c_z.jpg" }
      ) {
        childImageSharp {
          gatsbyImageData(
            layout: CONSTRAINED
            width: 960
            formats: [AUTO, WEBP]
            placeholder: BLURRED
          )
        }
      }
      gaTeamPhoto: file(relativePath: { eq: "GA_ACT_small.jpg" }) {
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
  `)

  return (
    <>
      <Section>
        <Title>How to get involved?</Title>

        <Columns>
          <WideColumn>
            <p>
              The&nbsp;
              <OutboundLink to="https://southeastaquatics.net/">
                Southeast Aquatic Resources Partnership
              </OutboundLink>
              &nbsp; (SARP) was formed by the Southeastern Association of Fish
              and Wildlife Agencies (SEAFWA) to protect aquatic resources across
              political boundaries as many of our river systems cross multiple
              jurisdictional boundaries.
            </p>
          </WideColumn>
          <NarrowColumn>
            <SARPLogo />
          </NarrowColumn>
        </Columns>
      </Section>
      <Section>
        <Columns>
          <NarrowColumn ml={[0, 0, '1rem']} mr={[0, 0, '1rem']}>
            <GatsbyImage
              image={forestStreamPhoto}
              alt="Sam D. Hamilton Noxubee National Wildlife Refuge"
            />

            <ImageCredits>
              Photo:{' '}
              <OutboundLink to="https://www.flickr.com/photos/usfwssoutheast/6882770647/in/album-72157629334467105/">
                Sam D. Hamilton Noxubee National Wildlife Refuge in Mississippi.
                U.S. Fish and Wildlife Service.
              </OutboundLink>
            </ImageCredits>
          </NarrowColumn>

          <WideColumn>
            <p>
              SARP works with partners to protect, conserve, and restore aquatic
              resources including habitats throughout the Southeast for the
              continuing benefit, use, and enjoyment of the American people.
              SARP is also one of the first Fish Habitat Partnerships under the
              the National Fish Habitat Partnership umbrella that works to
              conserve and protect the nation’s fisheries and aquatic systems
              through a network of 20 Fish Habitat Partnerships.
            </p>
          </WideColumn>
        </Columns>
      </Section>
      <Section>
        <Columns>
          <WideColumn>
            <p>
              SARP and partners have been working to build a community of
              practice surrounding barrier removal through the development of
              state-based Aquatic Connectivity Teams (ACTs). These teams create
              a forum that allows resource managers from all sectors to work
              together and share resources, disseminate information, and examine
              regulatory streamlining processes as well as project management
              tips and techniques. These teams are active in Arkansas, Florida,
              Georgia, North Carolina, and Tennessee.
              <br />
              <br />
              <Link to="/teams">
                Learn more about aquatic connectivity teams.
              </Link>
            </p>
          </WideColumn>

          <NarrowColumn>
            <GatsbyImage
              image={gaTeamPhoto}
              alt="Georgia Aquatic Connectivity Team"
            />
            <ImageCredits>
              Photo:{' '}
              <OutboundLink to="https://www.southeastaquatics.net/news/white-dam-removal-motivates-georgia-conservation-practitioners">
                Georgia Aquatic Connectivity Team
              </OutboundLink>
            </ImageCredits>
          </NarrowColumn>
        </Columns>
      </Section>

      <Section mt="4rem">
        <Columns>
          <WideColumn>
            <MinorTitle>Get involved!</MinorTitle>
            <p>
              You can help improve the inventory by sharing data, assisting with
              field reconnaissance to evaluate the impact of aquatic barriers,
              joining an <Link to="/teams">Aquatic Connectivity Team</Link>, or
              even by reporting issues with the inventory data in this tool.
              <br />
              <br />
              <a href="mailto:kat@southeastaquatics.net">Contact us</a> to learn
              more about how you can help improve aquatic connectivity in the
              Southeast.
            </p>
          </WideColumn>

          <NarrowColumn>
            <MinorTitle>Need Help?</MinorTitle>
            <p>
              If you are not able to get what you need from this tool or if you
              need to report an issue, please&nbsp;
              <a href="mailto:kat@southeastaquatics.net">let us know</a>!
            </p>
          </NarrowColumn>
        </Columns>
      </Section>
    </>
  )
}

export default SARP
