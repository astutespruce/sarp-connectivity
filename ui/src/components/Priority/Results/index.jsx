import React from 'react'
import PropTypes from 'prop-types'

import { Flex } from 'components/Grid'
import { HelpText } from 'components/Text'
import { useBarrierType } from 'components/Data'
import { countBy } from 'util/data'
import { formatNumber, capitalize } from 'util/format'
import styled, { themeGet } from 'style'

import Histogram from './Histogram'
import BackLink from '../BackLink'
import StartOverButton from '../StartOverButton'
import DownloadButton from './DownloadButton'
import { Wrapper, Header, Footer, Title, Content } from '../styles'

import { SCENARIOS } from '../../../../config/constants'

const Count = styled.div`
  color: ${themeGet('colors.grey.700')};
`

const InputContainer = styled(Flex).attrs({
  alignItems: 'center',
  my: '1rem',
  mr: '1rem',
})``

const Input = styled.input.attrs({
  type: 'range',
  min: '1',
  max: '20',
  step: '1',
})`
  flex: 1 1 auto;
  margin: 0 1rem;
`

const InputLabel = styled.div`
  font-size: 0.8rem;
  color: ${themeGet('colors.grey.700')};
  flex: 0 0 auto;
`

const Section = styled.div`
  &:not(:first-child) {
    margin-top: 2rem;
  }
`
const SectionHeader = styled.div`
  font-weight: bold;
`

const Results = ({
  downloadURL,
  scenario,
  rankData,
  tierThreshold,
  onSetTierThreshold,
  onBack,
}) => {
  const barrierType = useBarrierType()
  // const [tierThreshold, setTierThreshold] = useState(1)

  const handleDownloadClick = () => {
    console.log('download click')
  }

  const scenarioLabel =
    scenario === 'ncwc'
      ? 'combined network connectivity and watershed condition'
      : SCENARIOS[scenario].toLowerCase()

  // count records by tier
  const tierCounts = countBy(rankData, `${scenario}_tier`)

  const tiers = Array.from({ length: 20 }, (_, i) => i + 1)

  // convert to full histogram
  const counts = tiers.map(tier => tierCounts[tier] || 0)

  const handleThresholdChange = ({ target: { value } }) => {
    onSetTierThreshold(21 - value)
  }

  return (
    <Wrapper>
      <Header>
        <BackLink label="modify filters" onClick={onBack} />
        <Title>Explore results</Title>
        <Count>
          {formatNumber(rankData.length, 0)} prioritized {barrierType}
        </Count>
      </Header>

      <Content>
        <HelpText mb="2rem">
          {capitalize(barrierType)} are binned into tiers based on where they
          fall within the value range of the <b>{scenarioLabel}</b> score. Tier
          1 includes {barrierType} that fall within the top 5% of values for
          this score, and tier 20 includes {barrierType} that fall within the
          lowest 5% of values for this score.
        </HelpText>

        <Section>
          <SectionHeader>
            Choose top-ranked dams for display on map
          </SectionHeader>

          <InputContainer>
            <InputLabel>Lowest tier</InputLabel>
            <Input
              value={21 - tierThreshold}
              onChange={handleThresholdChange}
            />
            <InputLabel>Highest tier</InputLabel>
          </InputContainer>

          <HelpText>
            Use this slider to control the number of tiers visible on the map.
            Based on the number of {barrierType} visible for your area, you may
            be able to identify {barrierType} that are more feasible in the top
            several tiers than in the top-most tier.
          </HelpText>
        </Section>

        <Section>
          <SectionHeader>Number of dams by tier</SectionHeader>
          <Histogram counts={counts} threshold={tierThreshold} />
        </Section>
      </Content>

      <Footer>
        <StartOverButton />
        <DownloadButton
          label={`Download ${barrierType}`}
          downloadURL={downloadURL}
          onClick={handleDownloadClick}
        />
      </Footer>
    </Wrapper>
  )
}

Results.propTypes = {
  downloadURL: PropTypes.string.isRequired,
  scenario: PropTypes.string.isRequired,
  tierThreshold: PropTypes.number.isRequired,
  rankData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
    })
  ).isRequired,
  onSetTierThreshold: PropTypes.func.isRequired,
  onBack: PropTypes.func.isRequired,
}

export default Results
