import React from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Progress as ProgressBar, Text } from 'theme-ui'

const Progress = ({ progress, message }) => (
  <Box sx={{ py: '2rem' }}>
    <Text>{message ? `${message}...` : 'Extracting data...'}</Text>

    <Flex sx={{ alignItems: 'center' }}>
      <ProgressBar variant="styles.progress" max={100} value={progress} />
      <Text sx={{ ml: '1rem' }}>{progress}%</Text>
    </Flex>
  </Box>
)

Progress.propTypes = {
  progress: PropTypes.number,
  message: PropTypes.string,
}

Progress.defaultProps = {
  progress: 0,
  message: null,
}

export default Progress
