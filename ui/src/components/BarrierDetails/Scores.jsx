import React from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { Tab, Tabs } from 'components/Tabs'
import ScoresList from './ScoresList'
import { ScoresPropType } from './proptypes'

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
      <Text sx={{ fontSize: '1.25rem' }}>
        Compare to other {barrierType} in the
      </Text>
      <Tabs
        sx={{
          '>div:first-of-type': {
            bg: 'transparent',
          },
          '>div:first-of-type + div': {
            m: '-1rem -1rem 2rem',
          },
          button: {
            borderBottom: '0.25rem solid',
            borderBottomColor: 'transparent',
            bg: 'transparent',
            '&:hover': {
              borderBottomColor: 'grey.2',
            },
          },
          'button[data=is-active]': {
            borderBottomColor: 'blue.5',
          },
        }}
      >
        {availableTabs.map(({ id, label }) => (
          <Tab key={id} id={id} label={label}>
            <Text variant="help" sx={{ my: '2rem', fontSize: 0 }}>
              Tiers range from 20 (lowest) to 1 (highest).
            </Text>

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
