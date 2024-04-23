import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Heading, Text } from 'theme-ui'

import { SCENARIOS, barrierTypeLabels } from 'config'
import { useBarrierType } from 'components/Data'
import { Downloader } from 'components/Download'
import { ExpandableParagraph } from 'components/Text'
import { BackLink, StartOverButton } from 'components/Workflow'
import { countBy } from 'util/data'
import { formatNumber, capitalize } from 'util/format'

import Histogram from './Histogram'

const Results = ({
  config: rawConfig,
  scenario: rawScenario,
  resultsType,
  rankData,
  tierThreshold,
  onSetTierThreshold,
  onBack,
  onStartOver,
}) => {
  const barrierType = useBarrierType()
  const barrierTypeLabel = barrierTypeLabels[barrierType]
  const scenario = resultsType === 'perennial' ? `p${rawScenario}` : rawScenario

  let scenarioLabel = SCENARIOS[scenario].toLowerCase()
  if (scenario === 'ncwc') {
    scenarioLabel = 'combined network connectivity and watershed condition'
  } else if (scenario === 'pncwc') {
    scenarioLabel =
      'combined perennial network connectivity and watershed condition'
  }

  const config = {
    ...rawConfig,
    scenario,
  }

  // count records by tier
  const tierCounts = countBy(rankData, scenario)

  const tiers = Array.from({ length: 20 }, (_, i) => i + 1)

  // convert to full histogram
  const counts = tiers.map((tier) => tierCounts[tier] || 0)

  const handleThresholdChange = ({ target: { value } }) => {
    onSetTierThreshold(21 - value)
  }

  return (
    <Flex sx={{ flexDirection: 'column', height: '100%' }}>
      <Box
        sx={{
          flex: '0 0 auto',
          py: '1rem',
          pr: '0.5rem',
          pl: '1rem',
          borderBottom: '1px solid #DDD',
          bg: '#f6f6f2',
        }}
      >
        <BackLink label="modify filters" onClick={onBack} />
        <Heading as="h3">Explore results</Heading>
        <Text sx={{ color: 'grey.7' }}>
          {formatNumber(rankData.length, 0)} prioritized {barrierTypeLabel}
        </Text>
      </Box>

      <Box
        sx={{
          flex: '1 1 auto',
          pt: '0.5rem',
          px: '1rem',
          pb: '1rem',
          overflowY: 'auto',
          overflowX: 'hidden',
        }}
      >
        <ExpandableParagraph
          variant="help"
          snippet={`${capitalize(
            barrierTypeLabel
          )} are binned into tiers based on`}
        >
          <Text variant="help" sx={{ display: 'inline' }}>
            {capitalize(barrierTypeLabel)} are binned into tiers based on where
            they fall within the value range of the <b>{scenarioLabel}</b>{' '}
            score. Tier 1 includes {barrierTypeLabel} that fall within the top
            5% of values for this score, and tier 20 includes {barrierTypeLabel}{' '}
            that fall within the lowest 5% of values for this score.
          </Text>
        </ExpandableParagraph>

        <Box sx={{ mt: '1rem' }}>
          <Text sx={{ fontWeight: 'bold' }}>
            Choose top-ranked {barrierTypeLabel} for display on map
          </Text>

          <Flex
            sx={{
              alignItems: 'center',
              my: '1rem',
              mr: '1rem',
              span: {
                fontSize: 0,
                color: 'grey.7',
                flex: '0 0 auto',
              },
            }}
          >
            <Text>Lowest tier</Text>
            <input
              type="range"
              min="1"
              max="20"
              step="1"
              value={21 - tierThreshold}
              onChange={handleThresholdChange}
              style={{
                flex: '1 1 auto',
                margin: '0 1rem',
              }}
            />
            <Text>Highest tier</Text>
          </Flex>

          <Text variant="help" sx={{ fontSize: 0 }}>
            Use this slider to control the number of tiers visible on the map.
            Based on the number of {barrierTypeLabel} visible for your area, you
            may be able to identify {barrierTypeLabel} that are more feasible in
            the top several tiers than in the top-most tier.
          </Text>
        </Box>

        <Box sx={{ mt: '2rem' }}>
          <Text sx={{ fontWeight: 'bold' }}>
            Number of {barrierTypeLabel} by tier
          </Text>
          <Histogram counts={counts} threshold={tierThreshold} />
        </Box>
      </Box>

      <Flex
        sx={{
          alignItems: 'center',
          justifyContent: 'space-between',
          p: '1rem',
          flex: '0 0 auto',
          borderTop: '1px solid #DDD',
          bg: '#f6f6f2',
        }}
      >
        <StartOverButton onStartOver={onStartOver} />
        <Box>
          <Downloader
            barrierType={barrierType}
            label="Download prioritized barriers"
            config={config}
            customRank
          />
        </Box>
      </Flex>
    </Flex>
  )
}

Results.propTypes = {
  config: PropTypes.shape({
    summaryUnits: PropTypes.objectOf(PropTypes.array).isRequired,
    filters: PropTypes.object,
    scenario: PropTypes.string.isRequired,
  }).isRequired,
  scenario: PropTypes.string.isRequired,
  resultsType: PropTypes.string.isRequired,
  tierThreshold: PropTypes.number.isRequired,
  rankData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
    })
  ).isRequired,
  onSetTierThreshold: PropTypes.func.isRequired,
  onBack: PropTypes.func.isRequired,
  onStartOver: PropTypes.func.isRequired,
}

export default Results
