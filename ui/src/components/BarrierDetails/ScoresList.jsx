import React from 'react'
import { Box, Text } from 'theme-ui'
import { ScoresPropType } from './proptypes'
import ScoreChart from './ScoreChart'

const ScoresList = ({ nc, wc, ncwc }) => (
  <Box>
    <Text variant="help" sx={{ mt: '1rem', mb: '2rem', fontSize: 0 }}>
      Tiers range from 20 (lowest) to 1 (highest).
    </Text>
    <ScoreChart
      label="Network Connectivity Tier"
      score={nc.score}
      tier={nc.tier}
    />
    <ScoreChart
      label="Watershed Condition Tier"
      score={wc.score}
      tier={wc.tier}
    />
    <ScoreChart
      label="Network Connectivity & Watershed Condition Tier"
      score={ncwc.score}
      tier={ncwc.tier}
    />
  </Box>
)

ScoresList.propTypes = ScoresPropType.isRequired

export default ScoresList
