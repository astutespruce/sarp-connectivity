import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Heading, Paragraph, Text } from 'theme-ui'

import { useBarrierType } from 'components/Data'
import { Downloader } from 'components/Download'
import { countBy } from 'util/data'
import { formatNumber, capitalize } from 'util/format'

import Histogram from './Histogram'
import BackLink from '../BackLink'
import StartOverButton from '../StartOverButton'

import { SCENARIOS } from '../../../../config/constants'

const Results = ({
  config,
  scenario,
  rankData,
  tierThreshold,
  onSetTierThreshold,
  onBack,
}) => {
  const barrierType = useBarrierType()

  const scenarioLabel =
    scenario === 'ncwc'
      ? 'combined network connectivity and watershed condition'
      : SCENARIOS[scenario].toLowerCase()

  // count records by tier
  const tierCounts = countBy(rankData, `${scenario}_tier`)

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
          {formatNumber(rankData.length, 0)} prioritized {barrierType}
        </Text>
      </Box>

      <Box
        sx={{
          flex: '1 1 auto',
          p: '1rem',
          overflowY: 'auto',
          overflowX: 'hidden',
        }}
      >
        <Paragraph variant="help">
          {capitalize(barrierType)} are binned into tiers based on where they
          fall within the value range of the <b>{scenarioLabel}</b> score. Tier
          1 includes {barrierType} that fall within the top 5% of values for
          this score, and tier 20 includes {barrierType} that fall within the
          lowest 5% of values for this score.
        </Paragraph>

        <Box sx={{ mt: '2rem' }}>
          <Text sx={{ fontWeight: 'bold' }}>
            Choose top-ranked {barrierType} for display on map
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

          <Paragraph variant="help">
            Use this slider to control the number of tiers visible on the map.
            Based on the number of {barrierType} visible for your area, you may
            be able to identify {barrierType} that are more feasible in the top
            several tiers than in the top-most tier.
          </Paragraph>
        </Box>

        <Box sx={{ mt: '2rem' }}>
          <Text sx={{ fontWeight: 'bold' }}>
            Number of {barrierType} by tier
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
        <StartOverButton />
        <Downloader barrierType={barrierType} config={config} customRank />
      </Flex>
    </Flex>
  )
}

Results.propTypes = {
  config: PropTypes.shape({
    layer: PropTypes.string.isRequired,
    summaryUnits: PropTypes.arrayOf(
      PropTypes.shape({ id: PropTypes.string.isRequired })
    ).isRequired,
    filters: PropTypes.object,
    scenario: PropTypes.string.isRequired,
  }).isRequired,
  scenario: PropTypes.string.isRequired,
  tierThreshold: PropTypes.number.isRequired,
  rankData: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
    })
  ).isRequired,
  onSetTierThreshold: PropTypes.func.isRequired,
  onBack: PropTypes.func.isRequired,
}

export default Results
