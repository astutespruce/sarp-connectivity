import React from 'react'
import { Box, Text } from 'theme-ui'

import { Section } from 'components/Sidebar'

import { ScoresPropType } from './proptypes'
import ScoreChart from './ScoreChart'

const ScoresList = ({ nc, wc, ncwc, pnc, pwc, pncwc }) => (
  <Box sx={{ mx: '-0.5rem' }}>
    <Section title="Full networks">
      <Box sx={{ px: '1rem' }}>
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
    </Section>

    <Section title="Perennial reaches only" sx={{ mt: '2rem' }}>
      <Box sx={{ px: '1rem' }}>
        <ScoreChart
          label="Perennial Network Connectivity Tier"
          score={pnc.score}
          tier={pnc.tier}
        />
        <ScoreChart
          label="Perennial Watershed Condition Tier"
          score={pwc.score}
          tier={pwc.tier}
        />
        <ScoreChart
          label="Perennial Network Connectivity & Watershed Condition Tier"
          score={pncwc.score}
          tier={pncwc.tier}
        />
        <Text variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
          Note: perennial network connectivity is based on the total perennial
          (non-intermi ttent or ephemeral) length in a given network. Perennial
          watershed condition is based partly upon the percent of the perennial
          stream reaches that are not altered (canals / ditches).
        </Text>
      </Box>
    </Section>
  </Box>
)

ScoresList.propTypes = ScoresPropType.isRequired

export default ScoresList
