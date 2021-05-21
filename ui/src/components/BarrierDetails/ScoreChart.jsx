import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

// All scores are normalized on a 0-1 basis, with 0 being lowest value
const ScoreChart = ({ label, score, tier }) => (
  <Box
    sx={{
      '&:not(:first-of-type)': {
        mt: '3rem',
      },
    }}
  >
    <Text>{label}</Text>
    <Flex sx={{ alignItems: 'center', mt: '1rem' }}>
      <Text sx={{ flex: '0 0 auto', color: 'grey.7' }}>Low</Text>
      <Box
        sx={{
          flex: '1 1 auto',
          position: 'relative',
          mt: '0.25rem',
          mx: '1.25rem',
        }}
      >
        <Box
          sx={{
            height: '2px',
            bg: 'grey.2',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            pt: '0.25rem',
            top: '-1rem',
            width: '2rem',
            height: '2rem',
            borderRadius: '2rem',
            bg: 'grey.8',
            ml: '-1rem',
            textAlign: 'center',
            color: '#FFF',

            left: `${score}%`,
          }}
        >
          {tier}
        </Box>
      </Box>
      <Text sx={{ flex: '0 0 auto', color: 'grey.7' }}>High</Text>
    </Flex>
  </Box>
)

ScoreChart.propTypes = {
  label: PropTypes.string.isRequired,
  score: PropTypes.number.isRequired,
  tier: PropTypes.number.isRequired,
}

export default ScoreChart
