import React from 'react'
import PropTypes from 'prop-types'

import { Text, HelpText as BaseHelpText } from 'components/Text'
import BaseTabs, {
  Tab as BaseTab,
  ActiveButton,
  InactiveButton,
} from 'components/Tabs'
import styled, { themeGet } from 'style'
import ScoresList from './ScoresList'
import { ScoresPropType } from './proptypes'

const Title = styled(Text).attrs({ fontSize: '1.25rem' })``

const HelpText = styled(BaseHelpText).attrs({
  fontSize: '0.75rem',
  mb: '2rem',
})``

const Tabs = styled(BaseTabs)`
  ${ActiveButton}, ${InactiveButton} {
    border-left: none !important;
    border-right: none !important;
    border-top: none !important;
    background: #fff !important;
    padding: 0 0.5rem;
  }

  ${ActiveButton} {
    border-bottom: 3px solid ${themeGet('colors.primary.500')} !important;
  }

  ${InactiveButton} {
    border-bottom: 3px solid #fff;

    &:hover {
      border-bottom: 3px solid ${themeGet('colors.grey.500')};
    }
  }
`

const Tab = styled(BaseTab)``

const tabs = [
  { id: 'custom', label: 'Selected Area' },
  { id: 'state', label: 'State' },
  { id: 'se', label: 'Southeast' },
]

const Scores = ({ barrierType, scores }) => {
  const hasCustom = scores.custom && scores.custom.ncwc

  const availableTabs = hasCustom ? tabs : tabs.slice(1, tabs.length)

  return (
    <>
      <Title>Compare to other {barrierType} in the</Title>
      <Tabs>
        {availableTabs.map(({ id, label }) => (
          <Tab key={id} id={id} label={label}>
            <HelpText mt="2rem">
              Tiers range from 20 (lowest) to 1 (highest).
            </HelpText>

            <ScoresList {...scores[id]} />
          </Tab>
        ))}
      </Tabs>
    </>
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

export default Scores
