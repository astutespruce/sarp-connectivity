import React from 'react'
import { Image } from 'rebass'
import { FaExclamationTriangle } from 'react-icons/fa'

import { Text } from 'components/Text'
import { Link, OutboundLink } from 'components/Link'
import { Columns, Column as BaseColumn, Flex } from 'components/Grid'
import { HighlightBox } from 'components/Layout'
import styled, { themeGet } from 'style'
import DamPhoto from 'images/9272554306_b34bf886f4_z.jpg'
import NetworkGraphicSVG from 'images/functional_network.svg'

import {
  Section,
  Title,
  NarrowColumn,
  WideColumn,
  ImageCredits,
  Subtitle,
} from '../styles'

const Photo = styled(Image).attrs({ width: '100%' })`
  border-radius: 0.25rem;
`

const Column = styled(BaseColumn).attrs({ width: ['100%', '100%', '50%'] })``

const Header = styled(Flex).attrs({ alignItems: 'center' })`
  font-size: 1.5rem;
  line-height: 1.2;
  margin-bottom: 1rem;
`

const Step = styled(Flex)`
  color: #fff;
  background-color: ${themeGet('colors.grey.900')};
  border-radius: 5em;
  width: 2em;
  height: 2em;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 0.5rem;
  flex: 0 0 auto;
`

const List = styled.ul`
  li {
    margin: 0;
  }
`

const Note = styled(Text)`
  color: ${themeGet('colors.grey.600')};
`

const WarningIcon = styled(FaExclamationTriangle)`
  width: 1.5em;
  height: 1em;
  color: ${themeGet('colors.highlight.500')};
  display: inline;
  margin-right: 0.25em;
`

const NetworkGraphic = styled(Image).attrs({ src: NetworkGraphicSVG })`
  height: 30rem;
`

const Scoring = () => {
  return (
    <>
      <Section>
        <Title>How are barriers prioritized for removal?</Title>
        <Header>
          <Step>
            <div>1</div>
          </Step>
          <Subtitle>
            Aquatic barriers are identified and measured for their potential
            impact on aquatic organisms:
          </Subtitle>
        </Header>
        <Columns>
          <WideColumn>
            <p>
              Aquatic barriers are natural and human-made structures that impede
              the passage of aquatic organisms through the river network.
              <br />
              <br />
              They include:
            </p>
            <List>
              <li>Waterfalls</li>
              <li>Dams</li>
              <li>Road-related barriers</li>
            </List>
            <p>
              <br />
              Where possible, human-made barriers have been assessed using field
              reconnaissance to determine their likely impact on aquatic
              organisms as well as their feasibility of removal. You can
              leverage these characteristics to select a smaller number of
              barriers to prioritize.
            </p>
          </WideColumn>
          <NarrowColumn>
            <Photo src={DamPhoto} alt="Hartwell Dam" />
            <ImageCredits>
              <OutboundLink to="https://www.flickr.com/photos/savannahcorps/9272554306/">
                Hartwell Dam, Georgia. Billy Birdwell, U.S. Army Corps of
                Engineers.
              </OutboundLink>
            </ImageCredits>
          </NarrowColumn>
        </Columns>
      </Section>
      <Section>
        <Header>
          <Step>
            <div>2</div>
          </Step>
          <Subtitle>
            Aquatic barriers are measured for their impact on the aquatic
            network:
          </Subtitle>
        </Header>

        <Columns>
          <WideColumn>
            <p>
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
              &nbsp;(NHDPlus) for all areas except the lower Mississipi
              (hydrologic region 8), where the NHDPlus Medium Resolution version
              was the only one available. Where possible, their locations were
              manually inspected to verify their correct position on the aquatic
              network.
              <br />
              <br />
            </p>

            <Note>
              <WarningIcon />
              Note: due to limitations of existing data sources for aquatic
              networks, not all aquatic barriers can be correctly located on the
              aquatic networks. These barriers are not included in the network
              connectivity analysis and cannot be prioritized using this tool.
              However, these data can still be downloaded from this tool and
              used for offline analysis.
            </Note>
          </WideColumn>

          <NarrowColumn display={['none', 'unset']}>
            <NetworkGraphic />
          </NarrowColumn>
        </Columns>
      </Section>

      <Section>
        <Header>
          <Step>
            <div>3</div>
          </Step>
          <Subtitle>
            Barriers are characterized using metrics that describe the quality
            and status of their functional networks:
          </Subtitle>
        </Header>

        <Columns>
          <Column>
            <HighlightBox icon="length_high" title="Network Length">
              <p>
                Network length measures the amount of connected aquatic network
                length that would be added to the network by removing the
                barrier. Longer connected networks may provide more overall
                aquatic habitat for a wider variety of organisms and better
                support dispersal and migration.
                <br />
                <br />
                <Link to="/metrics/length">Read more...</Link>
              </p>
            </HighlightBox>
          </Column>
          <Column>
            <HighlightBox icon="size_classes_high" title="Network Complexity">
              <p>
                Network complexity measures the number of unique upstream size
                classes that would be added to the network by removing the
                barrier. A barrier that has upstream tributaries of different
                size classes, such as small streams, small rivers, and large
                rivers, would contribute a more complex connected aquatic
                network if it was removed.
                <br />
                <Link to="/metrics/complexity">Read more...</Link>
              </p>
            </HighlightBox>
          </Column>
        </Columns>

        <Columns style={{ marginTop: '2rem' }}>
          <Column>
            <HighlightBox icon="sinuosity_high" title="Network Sinuosity">
              <p>
                Network sinuosity measures the amount that the path of the river
                or stream deviates from a straight line. In general, rivers and
                streams that are more sinuous generally indicate those that have
                lower alteration from human disturbance such as channelization
                and diking.
                <br />
                <Link to="/metrics/sinuosity">Read more...</Link>
              </p>
            </HighlightBox>
          </Column>
          <Column>
            <HighlightBox icon="nat_landcover_high" title="Natural Landcover">
              <p>
                Natural landcover measures the amount of area within the
                floodplain of the upstream aquatic network that is in natural
                landcover. Rivers and streams that have a greater amount of
                natural landcover in their floodplain are more likely to have
                higher quality aquatic habitat.
                <br />
                <Link to="/metrics/landcover">Read more...</Link>
              </p>
            </HighlightBox>
          </Column>
        </Columns>
      </Section>

      <Section>
        <Header>
          <Step>
            <div>4</div>
          </Step>
          <Subtitle>
            Metrics are combined and ranked to create three scenarios for
            prioritizing barriers for removal:
          </Subtitle>
        </Header>
        <Columns>
          <Column>
            <HighlightBox title="Network Connectivity">
              <p>
                Aquatic barriers prioritized according to network connectivity
                are driven exclusively on the total amount of functional aquatic
                network that would be reconnected if a given dam was removed.
                This is driven by the&nbsp;
                <Link to="/metrics/length">network length</Link> metric. No
                consideration is given to other characteristics that measure the
                quality and condition of those networks.
              </p>
            </HighlightBox>
          </Column>

          <Column>
            <HighlightBox title="Watershed Condition">
              <p>
                Aquatic barriers prioritized according to watershed condition
                are driven by metrics related to the overall quality of the
                aquatic network that would be reconnected if a given dam was
                removed. It is based on a combination of&nbsp;
                <Link to="/metrics/complexity">network complexity</Link>
                ,&nbsp;
                <Link to="/metrics/sinuosity">network sinuosity</Link>,
                and&nbsp;
                <Link to="/metrics/landcover">
                  floodplain natural landcover
                </Link>
                . Each of these metrics is weighted equally.
              </p>
            </HighlightBox>
          </Column>
        </Columns>

        <HighlightBox
          title="Network Connectivity + Watershed Condition"
          mt="2rem"
        >
          <p>
            Aquatic barriers prioritized according to combined network
            connectivity and watershed condition are driven by both the length
            and quality of the aquatic networks that would be reconnected if
            these barriers are removed. <b>Network connectivity</b> and{' '}
            <b>watershed condition</b> are weighted equally.
          </p>
        </HighlightBox>
      </Section>

      <Section>
        <p>
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
        </p>
        <Note>
          <WarningIcon />
          Note: tiers are based on position within the range of observed scores
          for a given area. They are <i>not</i> based on the frequency of
          scores, such as percentiles, and therefore may have a highly uneven
          number of dams per tier depending on the area. In general, there are
          fewer barriers in the top tiers than there are in the bottom tiers.
          This is largely because many barriers share the same value for a given
          metric.
        </Note>
      </Section>
    </>
  )
}

export default Scoring
