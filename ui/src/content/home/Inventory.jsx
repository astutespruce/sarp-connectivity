import React from 'react'
import { Image } from 'rebass'

import { Link, OutboundLink } from 'components/Link'
import { HighlightBox as BaseHighlightBox } from 'components/Layout'
import { Columns } from 'components/Grid'
import styled from 'style'
import { formatNumber } from 'util/format'
import { useSummaryData } from 'components/Data'
import SARPLogoImage from 'images/sarp_logo.png'

import { Section, Title, NarrowColumn, WideColumn } from '../styles'

const HighlightBox = styled(BaseHighlightBox)`
  h3 {
    text-align: center;
  }
`

const Stats = styled.ul`
  list-style: none;
  font-size: 1.25rem;
  margin-left: 0;

  li {
    margin-bottom: 2rem;
  }
`

const SARPLogo = styled(Image).attrs({ src: SARPLogoImage, width: '100%' })`
  max-width: 300px;
`

const Inventory = () => {
  const { dams, barriers, miles } = useSummaryData()

  return (
    <Section>
      <Title>The Southeast Aquatic Barrier Inventory:</Title>
      <Columns>
        <WideColumn>
          <p>
            This inventory is a growing and living database of dams, culverts,
            and other road crossings compiled by the{' '}
            <OutboundLink to="https://southeastaquatics.net/">
              Southeast Aquatic Resources Partnership
            </OutboundLink>{' '}
            with the generous support from many partners and funders. The
            Inventory is the foundation of{' '}
            <OutboundLink to="https://southeastaquatics.net/sarps-programs/southeast-aquatic-connectivity-assessment-program-seacap">
              SARP&apos;s Connectivity Program
            </OutboundLink>{' '}
            because it empowers{' '}
            <Link to="/teams">Aquatic Connectivity Teams</Link> and other
            collaborators with the best available information on aquatic
            barriers. The inventory directly supports prioritization of barriers
            by including metrics that describe network connectivity, landscape
            condition, and presence of threatened and endangered aquatic
            organisms.
            <br />
            <br />
            This inventory consists of datasets from local, state, and federal
            partners. It is supplemented with input from partners with on the
            ground knowledge of specific structures.{' '}
            <Link to="#example">
              See an example of how the inventory can assist local partners to
              identify and prioritize barriers for removal.
            </Link>
            <br />
            <br />
            The information on barriers is not complete or comprehensive across
            the region, and depends on the availability and completeness of
            existing data and level of partner feedback. Some areas of the
            region are more complete than others but none should be considered
            100% complete.
          </p>
        </WideColumn>

        <NarrowColumn>
          <HighlightBox title="At a Glance" icon="">
            <Stats>
              <li>
                <b>14</b> states and Puerto Rico
              </li>
              <li>
                <b>{formatNumber(dams, 0)}</b> dams
              </li>
              <li>
                <b>{formatNumber(barriers, 0)}</b> road-related barriers
                assessed for impact to aquatic organisms
              </li>
              <li>
                <b>{formatNumber(miles, 1)}</b> miles of connected aquatic
                network length, on average
              </li>
            </Stats>

            <SARPLogo />
          </HighlightBox>
        </NarrowColumn>
      </Columns>
    </Section>
  )
}

export default Inventory
