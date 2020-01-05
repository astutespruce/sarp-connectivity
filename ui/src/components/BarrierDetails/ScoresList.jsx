import React from 'react'

import { ScoresPropType } from './proptypes'
import ScoreChart from './ScoreChart'

const ScoresList = ({ nc, wc, ncwc }) => (
  <div>
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
  </div>
)

ScoresList.propTypes = ScoresPropType.isRequired

export default ScoresList
