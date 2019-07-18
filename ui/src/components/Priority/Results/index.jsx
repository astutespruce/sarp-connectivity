import React, { useState } from 'react'
import PropTypes from 'prop-types'
// import debounce from "lodash.debounce"

import {Flex} from 'components/Grid'
import { Text, HelpText } from 'components/Text'
import { useBarrierType } from 'components/Data'
import {countBy} from 'util/data'
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

const InputContainer = styled(Flex).attrs({ alignItems: 'center', my: '1rem', mr: '1rem' })``

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
  // logDownload,
  onBack,
}) => {
  const barrierType = useBarrierType()

  // TODO: proper home and value for state
  const [tierThreshold, setTierThreshold] = useState(0)

  const handleDownloadClick = () => {
    console.log('download click')
  }

  const scenarioLabel =
    scenario === 'ncwc'
      ? 'combined network connectivity and watershed condition'
      : SCENARIOS[scenario].toLowerCase()


      window.rankData = rankData

      // count records by tier
      const tierCounts = countBy(rankData, `${scenario}_tier`)

  const tiers = Array.from({length: 20}, (_,i) => i + 1)

  // convert to full histogram
  const counts = tiers.map(tier => tierCounts[tier] || 0)

  const handleThresholdChange = ({ target: { value } }) => {
    // TODO: debounce
    // debounce(() => setTierThreshold(21 - value), 50)()
    setTierThreshold(21 - value)
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
        <HelpText mb='2rem'>
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

  //   return (
  //     <>
  //       <div id="SidebarHeader">
  //         <button
  //           className="link link-back"
  //           type="button"
  //           onClick={onBack}
  //         >
  //           <span className="fa fa-reply" />
  //           &nbsp; modify filters
  //         </button>
  //         <h4 className="title is-4 no-margin">Explore results</h4>
  //         <div className="has-text-grey flex-container flex-justify-space-between">
  //           <div>
  //             {formatNumber(totalCount, 0)} prioritized {type}
  //           </div>
  //         </div>
  //       </div>
  //       <div id="SidebarContent">
  // <p className="has-text-grey">
  //   {type.slice(0, 1).toUpperCase() + type.slice(1)} are binned into tiers
  //   based on where they fall within the value range of the{' '}
  //   <b>{scenarioLabel}</b> score. Tier 1 includes {type} that fall within
  //   the top 5% of values for this score, and tier 20 includes {type} that
  //   fall within the lowest 5% of values for this score.
  //   <br />
  //   <br />
  // </p>

  //         <div style={{ margin: '2rem 0' }}>
  //           <h6 className="title is-6 no-margin">
  //             Choose top-ranked dams for display on map
  //           </h6>

  //           <div className="flex-container" style={{ margin: '1rem' }}>
  //             <div className="is-size-7">Lowest tier</div>
  //             <input
  // type="range"
  // min="1"
  // max="20"
  // step="1"
  //               className="flex-grow"
  //               value={21 - tierThreshold}
  //               onChange={handleThresholdChange}
  //             />
  //             <div className="is-size-7">Highest tier</div>
  //           </div>
  //           <p className="has-text-grey">
  // Use this slider to control the number of tiers visible on the map.
  // Based on the number of {type} visible for your area, you may be able
  // to identify {type} that are more feasible in the top several tiers
  // than in the top-most tier.
  //           </p>
  //         </div>

  //         <h6 className="title is-6 no-margin">Number of dams by tier</h6>

  //         <Histogram counts={counts} threshold={tierThreshold} />
  //       </div>

  //       <div id="SidebarFooter">
  //         <div className="flex-container flex-justify-center flex-align-center">
  //           <StartOverButton />

  //           <a
  //             href={`${API_HOST}/api/v1/${type}/csv/${layer}?${apiQueryParams(
  //               summaryUnits,
  //               filters
  //             )}`}
  //             target="_blank"
  //             rel="noopener noreferrer"
  //             className="button is-info is-medium"
  //             onClick={() => logDownload()}
  //           >
  //             <i className="fa fa-download" style={{ marginRight: '0.25em' }} />
  //             Download {barrierType}
  //           </a>
  //         </div>
  //       </div>
  //     </>
  //   )
}

Results.propTypes = {
  downloadURL: PropTypes.string.isRequired,
  scenario: PropTypes.string.isRequired,
  rankData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ).isRequired,
  // logDownload: PropTypes.func.isRequired,
  onBack: PropTypes.func.isRequired,
}

export default Results
