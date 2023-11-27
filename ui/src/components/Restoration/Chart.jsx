import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { barrierTypeLabels } from 'config'
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
        damsGainMiles = 0,
        smallBarriers = 0,
        smallBarriersGainMiles = 0,
      }) => {
        if (metric === 'count') {
          let total = dams + smallBarriers
          if (barrierType === 'dams') {
            total = dams
          } else if (barrierType === 'small_barriers') {
            total = smallBarriers
          }

          return {
            label,
            dams,
            smallBarriers,
            total,
          }
        }

        let total = damsGainMiles + smallBarriersGainMiles
        if (barrierType === 'dams') {
          total = damsGainMiles
        } else if (barrierType === 'small_barriers') {
          total = smallBarriersGainMiles
        }

        return {
          label,
          dams: damsGainMiles,
          smallBarriers: smallBarriersGainMiles,
          total,
        }
      }
    )
    // only show unknown when present
    .filter(({ label, total }) => label !== 'unknown' || total > 0)

  const max = Math.max(...entries.map(({ total }) => total))

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
          gap: '0.5rem',
          alignItems: 'center',
          fontSize: 1,
          borderBottom: '1px solid',
          borderBottomColor: 'grey.1',
          pb: '0.25em',
        }}
      >
        <Text sx={{ color: 'grey.7' }}>Show total:</Text>
        <Text
          sx={{
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
          <sup>*</sup>
        </Text>
        <Text>|</Text>
        <Text
          sx={{
            fontWeight: metric === 'count' ? 'bold' : 'inherit',
            color: metric === 'count' ? 'highlight' : 'grey.7',
            cursor: 'pointer',
            '&:hover': {
              color: metric === 'count' ? 'highlight' : 'text',
            },
          }}
          onClick={() => onChangeMetric('count')}
        >
          count
        </Text>
      </Flex>

      <Box
        sx={{
          fontSize: 1,
          mr: `${formatNumber(max).length + 2}em`,
          py: '0.5em',
        }}
      >
        {entries.map(({ label, dams, smallBarriers, total }) => (
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
                {formatNumber(total, 0)}{' '}
                {metric === 'gainmiles' ? 'miles' : null}
              </Text>
            </Flex>
          </Flex>
        ))}
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
