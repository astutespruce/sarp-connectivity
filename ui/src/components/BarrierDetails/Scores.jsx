import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Text } from 'theme-ui'

import { Link } from 'components/Link'
import { Tab, Tabs } from 'components/Tabs'
import { barrierTypeLabels } from 'config'
import { groupBy } from 'util/data'
import ScoresList from './ScoresList'
import { ScoresPropType } from './proptypes'

const tabs = [
  { id: 'custom', label: 'Selected Area' },
  { id: 'state', label: 'State' },
]

const tabIndex = groupBy(tabs, 'id')

const Scores = ({ barrierType, scores }) => {
  console.log('scores', scores)

  const barrierTypeLabel = barrierTypeLabels[barrierType]
  const prioritizePath =
    barrierType === 'dams' ? '/priority/dams' : '/priority/barriers'

  const hasCustomTiers = scores.custom && scores.custom.ncwc
  const hasStateTiers = scores.state && scores.state.ncwc

  const availableTabs = []
  if (hasCustomTiers) {
    availableTabs.push(tabs[0])
  }
  if (hasStateTiers) {
    availableTabs.push(tabs[1])
  }

  const [tab, setTab] = useState(
    availableTabs.length > 0 ? availableTabs[0].id : null
  )

  const handleTabChange = (id) => {
    setTab(id)
  }

  if (!(hasStateTiers || hasCustomTiers)) {
    return (
      <Text sx={{ color: 'grey.8' }}>
        State-level ranks are not available for {barrierTypeLabel}. Instead, you
        can <Link to={prioritizePath}>prioritize {barrierTypeLabel}</Link> for a
        specific area.
      </Text>
    )
  }

  return (
    <>
      <Text variant="help" sx={{ mb: '1rem', fontSize: 0 }}>
        Tiers range from 20 (lowest) to 1 (highest).
      </Text>

      {tab !== null ? (
        <Text>
          Compared to other {barrierTypeLabels[barrierType]} in the
          {availableTabs.length === 1
            ? ` ${tabIndex[tab].label.toLowerCase()}:`
            : null}
        </Text>
      ) : null}

      {availableTabs.length > 1 ? (
        <Tabs
          sx={{
            borderTop: '2px solid',
            borderTopColor: 'grey.2',
            mx: '-0.75rem',
          }}
          onChange={handleTabChange}
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
    state: ScoresPropType,
    custom: ScoresPropType,
  }).isRequired,
}

export default Scores
