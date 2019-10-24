import React from 'react'
import { Link } from 'components/Link'
import { HighlightBox } from 'components/Layout'
import { Columns, Column as BaseColumn } from 'components/Grid'
import styled from 'style'
import { Section, Title, LargeText } from '../styles'

const Column = styled(BaseColumn).attrs({
  width: ['100%', '100%', '33%'],
  px: '0.5rem',
})`
  display: flex;
  flex-direction: column;
`

const Top = () => {
  return (
    <>
      <LargeText>
        Aquatic connectivity is essential. Fish and other aquatic organisms
        depend on high quality, connected river networks. A legacy of human use
        of river networks have left them fragmented by barriers such as dams and
        culverts. Fragmentation prevents species from dispersing and accessing
        habitats required for their persistence through changing conditions.
        <br />
        <br />
        Recently improved inventories of aquatic barriers enable us to describe,
        understand, and prioritize them for removal, restoration, and
        mitigation. Through this tool and others, we empower you by providing
        information on documented barriers and standardized methods by which to
        prioritize barriers of interest for restoration efforts.
      </LargeText>

      <Section>
        <Title>
          Enhancing aquatic connectivity by empowering people with actionable
          data:
        </Title>

        <Columns flexWrap={['wrap']}>
          <Column>
            <HighlightBox title="Inventory" icon="dam">
              The aquatic barrier inventory is the foundation for identifying
              and prioritizing aquatic connectivity projects with partners. It
              provides essential information about the location, status, and
              characteristics of potential aquatic barriers.
              <br />
              <br />
              Scroll down for more information.
            </HighlightBox>
          </Column>

          <Column>
            <HighlightBox title="Prioritization" icon="prioritize">
              In order to maximize partner effort and return on investment,
              aquatic barriers are prioritized based on their contribution to
              the aquatic network if removed. Quantitative metrics provide
              actionable information to assist barrier removal projects.
              <br />
              <br />
              <Link to="/#prioritize">Read more...</Link>
            </HighlightBox>
          </Column>

          <Column>
            <HighlightBox title="Teams" icon="team">
              Aquatic connectivity teams make barrier removal projects a
              reality. By combining effort across organizations and
              jurisdictions, partners work together to identify, prioritize, and
              implement barrier removal projects.
              <br />
              <br />
              <br />
              <Link to="/teams">Read more...</Link>
            </HighlightBox>
          </Column>
        </Columns>
      </Section>
    </>
  )
}

export default Top
