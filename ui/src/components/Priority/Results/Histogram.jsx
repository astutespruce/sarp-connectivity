/* eslint-disable react/no-array-index-key */
import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { pointColors } from 'config'
import { formatNumber } from 'util/format'

const Histogram = ({ counts, threshold }) => {
  const max = Math.max(...counts)

  const labelWidth = max.toString().length * 0.75

  return (
    <Box sx={{ flex: '1 1 auto', py: '0.25rem' }}>
      {counts.map((count, i) => (
        <Flex
          key={`${i}-${count}`}
          sx={{
            alignItems: 'center',
            mb: '0.25rem',
            color: i + 1 <= threshold ? pointColors.topRank.color : 'grey.7',
          }}
        >
          <Text
            sx={{
              width: '4rem',
              fontSize: 0,
              mr: '0.25rem',
              textAlign: 'right',
            }}
          >
            Tier {i + 1}
          </Text>
          <Flex
            sx={{
              alignItems: 'center',
              flex: '1 1 auto',
              py: '0.1em',
              mr: '0.25rem',
              borderLeft: '1px solid #AAA',
            }}
          >
            <Box
              sx={{
                height: '1rem',
                bg:
                  i + 1 <= threshold
                    ? pointColors.topRank.color
                    : pointColors.lowerRank.color,
                width: `calc(${(100 * count) / max}% - ${labelWidth}em)`,
              }}
            />
            <Text
              sx={{
                width: '4rem',
                fontSize: 0,
                ml: '0.25rem',
              }}
            >
              {formatNumber(count, 0)}
            </Text>
          </Flex>
        </Flex>
      ))}
    </Box>
  )
}

Histogram.propTypes = {
  counts: PropTypes.arrayOf(PropTypes.number).isRequired,
  threshold: PropTypes.number.isRequired,
}

export default Histogram
