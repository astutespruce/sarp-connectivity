import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { Tab, Tabs } from 'components/Tabs'
import ScoresList from './ScoresList'
import { ScoresPropType } from './proptypes'
import { barrierTypeLabels } from '../../../config/constants'

const tabs = [
  { id: 'custom', label: 'Selected Area' },
  { id: 'state', label: 'State' },
]

const Scores = ({ barrierType, scores }) => {
  const hasCustom = scores.custom && scores.custom.ncwc

  const availableTabs = []
  if (hasCustom) {
    availableTabs.push(tabs[0])
  }
  availableTabs.push(tabs[1])

  return (
    <>
      <Text variant="help" sx={{ mb: '1rem', fontSize: 0 }}>
        Tiers range from 20 (lowest) to 1 (highest).
      </Text>
      <Text>
        Compare to other {barrierTypeLabels[barrierType]} in the{' '}
        {availableTabs.length === 1 ? 'state:' : null}
      </Text>

      {availableTabs.length > 1 ? (
        <Tabs
          sx={{
            borderTop: '2px solid',
            borderTopColor: 'grey.2',
            mx: '-0.75rem',
          }}
        >
          {availableTabs.map(({ id, label }) => (
            <Tab key={id} id={id} label={label}>
              <ScoresList {...scores[id]} />
            </Tab>
          ))}
        </Tabs>
      ) : (
        <ScoresList {...scores[availableTabs[0].id]} />
      )}
    </>
  )
}

Scores.propTypes = {
  barrierType: PropTypes.string.isRequired,
  scores: PropTypes.shape({
    se: ScoresPropType,
    state: ScoresPropType.isRequired,
    custom: ScoresPropType,
  }).isRequired,
}

export default Scores
