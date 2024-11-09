import React from 'react'
import { Box, Text } from 'theme-ui'

import { Section } from 'components/Sidebar'

import { ScoresPropType } from './proptypes'
import ScoreChart from './ScoreChart'

const ScoresList = ({ nc, wc, ncwc, pnc, pwc, pncwc, mnc, mwc, mncwc }) => (
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
      <Text variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
        Note: network connectivity is based on the total perennial length in a
        given network. Watershed condition is based on the percent of the total
        length of stream reaches in the network that are not altered (canals /
        ditches), the number of unique stream size classes, and the percent of
        natural landcover in the floodplains.
      </Text>
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
          (non-intermittent or ephemeral) length in a given network. Perennial
          watershed condition is based on the percent of the total length of
          perennial stream reaches that are not altered (canals / ditches), the
          number of unique stream size classes in perennial reaches, and the
          percent of natural landcover in the floodplains for the full network.
        </Text>
      </Box>
    </Section>
    <Section title="Mainstem networks" sx={{ mt: '2rem' }}>
      <Box sx={{ px: '1rem' }}>
        <ScoreChart
          label="Mainstem Network Connectivity Tier"
          score={mnc.score}
          tier={mnc.tier}
        />
        <ScoreChart
          label="Mainstem Watershed Condition Tier"
          score={mwc.score}
          tier={mwc.tier}
        />
        <ScoreChart
          label="Mainstem Network Connectivity & Watershed Condition Tier"
          score={mncwc.score}
          tier={mncwc.tier}
        />
        <Text variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
          Note: mainstem network connectivity is based on the total mainstem
          network length in a given network. Mainstem watershed condition is
          based on the percent of the total length of stream reaches in the
          mainstem network that are not altered (canals / ditches), the number
          of unique stream size classes in the mainstem network, and the percent
          of natural landcover in the floodplains for the full network.
        </Text>
      </Box>
    </Section>
  </Box>
)

ScoresList.propTypes = ScoresPropType.isRequired

export default ScoresList
