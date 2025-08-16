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
  { id: 'huc8', label: 'Subbasin' },
]

const tabIndex = groupBy(tabs, 'id')

const Scores = ({ networkType, scores }) => {
  const hasCustomTiers = scores.custom && scores.custom.ncwc
  const hasStateTiers = scores.state && scores.state.ncwc
  const hasHUC8Tiers = scores.huc8 && scores.huc8.ncwc

  const availableTabs = []
  if (hasCustomTiers) {
    availableTabs.push(tabs[0])
  }
  if (hasStateTiers) {
    availableTabs.push(tabs[1])
  }
  if (hasHUC8Tiers) {
    availableTabs.push(tabs[2])
  }

  const [tab, setTab] = useState(
    availableTabs.length > 0 ? availableTabs[0].id : null
  )

  const handleTabChange = (id) => {
    setTab(id)
  }

  if (!(hasStateTiers || hasHUC8Tiers || hasCustomTiers)) {
    return (
      <Text sx={{ color: 'grey.8' }}>
        State-level ranks are not available for this network type because there
        are not yet sufficient assessed road-related barriers at the state level
        for all states. Instead, you can <Link to="/priority">prioritize</Link>{' '}
        barriers to calculate ranks for a selected area.
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
          Compared to other {barrierTypeLabels[networkType]} in the
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
  networkType: PropTypes.string.isRequired,
  scores: PropTypes.shape({
    state: ScoresPropType,
    huc8: ScoresPropType,
    custom: ScoresPropType,
  }).isRequired,
}

export default Scores
