import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { barrierTypeLabels } from 'config'
import { sum } from 'util/data'
import { formatNumber } from 'util/format'

const Chart = ({
  barrierType,
  removedBarriersByYear,
  metric,
  onChangeMetric,
}) => {
  const entries = removedBarriersByYear
    .map(
      ({
        label,
        dams = 0,
        damsNoNetwork = 0,
        damsGainMiles = 0,
        smallBarriers = 0,
        smallBarriersNoNetwork = 0,
        smallBarriersGainMiles = 0,
      }) => {
        let totalCount = dams + smallBarriers

        let totalNoNetworkCount = damsNoNetwork + smallBarriersNoNetwork
        let totalGainMiles = damsGainMiles + smallBarriersGainMiles
        if (barrierType === 'dams') {
          totalCount = dams
          totalNoNetworkCount = damsNoNetwork
          totalGainMiles = damsGainMiles
        } else if (barrierType === 'small_barriers') {
          totalCount = smallBarriers
          totalNoNetworkCount = smallBarriersNoNetwork
          totalGainMiles = smallBarriersGainMiles
        }

        const out = {
          label,
          totalCount,
          totalNoNetworkCount,
          totalGainMiles,
          dams,
          smallBarriersGainMiles,
        }

        if (metric === 'gainmiles') {
          out.dams = damsGainMiles
          out.smallBarriers = smallBarriersGainMiles
        }

        return out
      }
    )
    // only show unknown when present
    .filter(({ label, totalCount }) => label !== 'unknown' || totalCount > 0)

  const max = Math.max(
    ...entries.map(({ totalCount, totalGainMiles }) =>
      metric === 'gainmiles' ? totalGainMiles : totalCount
    )
  )

  const totalNoNetworkCount = sum(
    entries.map(
      ({ totalNoNetworkCount: yearNoNetworkCount }) => yearNoNetworkCount
    )
  )

  if (max === 0) {
    return null
  }

  const showDams = barrierType === 'dams' || barrierType === 'combined_barriers'
  const showSmallBarriers =
    barrierType === 'small_barriers' || barrierType === 'combined_barriers'

  return (
    <>
      <Flex
        sx={{
          mt: '0.5rem',
          alignItems: 'center',
          fontSize: 0,
          color: 'grey.7',
          borderBottom: '1px solid',
          borderBottomColor: 'grey.2',
        }}
      >
        <Text
          sx={{
            flex: '0 0 6rem',
            textAlign: 'right',
            pr: '0.75em',
            pb: '0.25rem',
          }}
        >
          year removed
        </Text>
        <Flex
          sx={{
            gap: '0.5rem',
            alignItems: 'center',
            borderLeft: '1px solid',
            borderLeftColor: 'grey.2',
            pl: '0.5rem',
            pb: '0.25rem',
          }}
        >
          <Text sx={{ flex: '0 0 auto', color: 'grey.7' }}>show:</Text>
          <Text
            sx={{
              flex: '0 0 auto',
              fontWeight: metric === 'gainmiles' ? 'bold' : 'inherit',
              color: metric === 'gainmiles' ? 'highlight' : 'grey.7',
              cursor: 'pointer',
              '&:hover': {
                color: metric === 'gainmiles' ? 'highlight' : 'text',
              },
            }}
            onClick={() => onChangeMetric('gainmiles')}
          >
            miles gained
          </Text>
          <Text sx={{ flex: '0 0 auto', color: 'grey.7' }}>|</Text>
          <Text
            sx={{
              flex: '0 0 auto',
              fontWeight: metric === 'count' ? 'bold' : 'inherit',
              color: metric === 'count' ? 'highlight' : 'grey.7',
              cursor: 'pointer',
              '&:hover': {
                color: metric === 'count' ? 'highlight' : 'text',
              },
            }}
            onClick={() => onChangeMetric('count')}
          >
            number removed
          </Text>
        </Flex>
      </Flex>

      <Box
        sx={{
          fontSize: 1,
          mr: `${formatNumber(max).length + 2}em`,
          mb: '0.5em',
        }}
      >
        {entries.map(
          ({
            label,
            dams,
            smallBarriers,
            totalCount,
            totalGainMiles,
            totalNoNetworkCount: yearNoNetworkCount,
          }) => (
            <Flex key={label} sx={{ alignItems: 'center' }}>
              <Text sx={{ flex: '0 0 6rem', textAlign: 'right', pr: '0.75em' }}>
                {label}
              </Text>
              <Flex
                sx={{
                  flex: '1 1 auto',
                  alignItems: 'center',
                  borderLeft: '1px solid',
                  borderLeftColor: 'grey.2',
                  py: '0.25rem',
                }}
              >
                {showDams ? (
                  <Box
                    sx={{
                      flex: `0 0 ${(100 * dams) / max}%`,
                      height: '1em',
                      bg: 'blue.8',
                    }}
                  />
                ) : null}
                {showSmallBarriers ? (
                  <Box
                    sx={{
                      flex: `0 0 ${(100 * smallBarriers) / max}%`,
                      height: '1em',
                      bg: showDams ? 'blue.2' : 'blue.8',
                    }}
                  />
                ) : null}
                <Text
                  sx={{
                    flex: '0 0 auto',
                    fontSize: 0,
                    color: 'grey.7',
                    pl: '0.25rem',
                  }}
                >
                  {metric === 'gainmiles'
                    ? `${formatNumber(totalGainMiles)} miles`
                    : formatNumber(totalCount)}
                  {yearNoNetworkCount ? <sup>*</sup> : null}
                </Text>
              </Flex>
            </Flex>
          )
        )}
      </Box>

      {barrierType === 'combined_barriers' ? (
        <Flex
          sx={{
            gap: '2rem',
            fontSize: 0,
            justifyContent: 'center',
            borderTop: '1px solid',
            borderTopColor: 'grey.1',
            pt: '0.25em',
          }}
        >
          <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
            <Box
              sx={{
                flex: '0 0 auto',
                width: '1em',
                height: '1em',
                bg: 'blue.8',
              }}
            />
            <Box sx={{ flex: '1 1 auto' }}>{barrierTypeLabels.dams}</Box>
          </Flex>
          <Flex sx={{ alignItems: 'center', gap: '0.25rem' }}>
            <Box
              sx={{
                flex: '0 0 auto',
                width: '1em',
                height: '1em',
                bg: 'blue.2',
              }}
            />
            <Box sx={{ flex: '1 1 auto' }}>
              {barrierTypeLabels.small_barriers}
            </Box>
          </Flex>
        </Flex>
      ) : null}

      {totalNoNetworkCount > 0 ? (
        <Text variant="help" sx={{ mt: '1rem', fontSize: 0 }}>
          <sup>*</sup> includes {formatNumber(totalNoNetworkCount)}{' '}
          {showDams ? barrierTypeLabels.dams : null}{' '}
          {showDams && showSmallBarriers ? ' and / or ' : null}{' '}
          {showSmallBarriers ? barrierTypeLabels.smallBarriers : null} that
          could not be correctly located on the aquatic network or were
          otherwise excluded from the analysis; these contribute toward the
          count but not the miles gained.
        </Text>
      ) : null}
    </>
  )
}

Chart.propTypes = {
  barrierType: PropTypes.string.isRequired,
  removedBarriersByYear: PropTypes.arrayOf(
    PropTypes.shape({
      dams: PropTypes.number.isRequired,
      damsGainMiles: PropTypes.number.isRequired,
      smallBarriers: PropTypes.number.isRequired,
      smallBarriersGainMiles: PropTypes.number.isRequired,
    })
  ).isRequired,
  metric: PropTypes.string.isRequired, // gainmiles or count
  onChangeMetric: PropTypes.func.isRequired,
}

Chart.defaultProps = {}

export default Chart
