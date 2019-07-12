// state: summaryunit, metrics expanded.  TODO: put these in global state otherwise we have issues

import React, { useState } from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText as BaseHelpText } from 'components/Text'
import { Tab, TabContainer } from 'components/Tabs'
import styled from 'style'
import ScoresList from './ScoresList'
import { ScoresPropType } from './proptypes'

const Wrapper = styled.div``

const Title = styled(Text).attrs({ fontSize: '1.25rem' })``

const HelpText = styled(BaseHelpText).attrs({ fontSize: '0.75rem', mb: '2rem' })``

const tabs = [
  { id: 'custom', label: 'Selected Area' },
  { id: 'state', label: 'State' },
  { id: 'se', label: 'Southeast' },
]

const Scores = ({ barrierType, scores }) => {
  // const [tab, setTab] = useState('custom')

  const hasCustom = scores.custom && scores.custom.ncwc

  const availableTabs = hasCustom ? tabs : tabs.slice(1, tabs.length)

  //   const handleCustomClick = () => setTab('custom')
  //   const handleStateClick = () => setTab('state')
  //   const handleRegionclick = () => setTab('se')

  return (
    <Wrapper>
      <Title>Compare to other {barrierType} in the</Title>
      {/* <div className="tabs">
        <ul className="flex-justify-center">
          {hasCustom ? (
            <li className={tab === 'custom' ? 'is-active' : null}>
              <a onClick={handleCustomClick}>Selected Area</a>
            </li>
          ) : null}
          <li className={tab === 'state' ? 'is-active' : null}>
            <a onClick={handleStateClick}>State</a>
          </li>
          <li className={tab === 'se' ? 'is-active' : null}>
            <a onClick={handleRegionclick}>Southeast</a>
          </li>
        </ul>
      </div> */}
      <TabContainer>
        {availableTabs.map(({ id, label }) => (
          <Tab key={id} id={id} label={label}>
            <HelpText>Tiers range from 1 (highest) to 20 (lowest).</HelpText>

            <ScoresList {...scores[id]} />
          </Tab>
        ))}
      </TabContainer>
      {/* 
    //   <HelpText>
    //     Tiers range from 1 (highest) to 20 (lowest).
    //   </HelpText>

    //   <ScoresList {...scores[tab]} /> */}
    </Wrapper>
  )
}

Scores.propTypes = {
  barrierType: PropTypes.string.isRequired,
  scores: PropTypes.shape({
    se: ScoresPropType.isRequired,
    state: ScoresPropType.isRequired,
    custom: ScoresPropType,
  }).isRequired,
}

// const mapStateToProps = globalState => ({
//   type: globalState.get('priority').get('type'),
//   tab: globalState.get('details').get('unit'),
// })

// export default connect(
//   mapStateToProps,
//   { setTab: setDetailsUnit }
// )(Scores)

export default Scores
