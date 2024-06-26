import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { Checkbox } from 'components/Button'
import { barrierTypeLabels } from 'config'

const Options = ({ barrierType, options, customRank, onChange }) => {
  const { includeUnranked } = options
  const barrierTypeLabel = barrierTypeLabels[barrierType]

  const handleIncludeUnrankedChange = () => {
    onChange({
      ...options,
      includeUnranked: !includeUnranked,
    })
  }

  return (
    <Box sx={{ alignItems: 'flex-start', mt: '1rem' }}>
      <Checkbox
        id="includeUnranked"
        label={`Include unranked ${barrierTypeLabel}?`}
        checked={includeUnranked}
        onChange={handleIncludeUnrankedChange}
        sx={{
          fontWeight: 'bold',
          fontSize: 3,
        }}
      />

      <Text sx={{ color: 'grey.8', mt: '0rem', ml: '1.8rem' }}>
        This will include {barrierTypeLabel} within your selected geographic
        area that were not prioritized in the analysis. These include any{' '}
        {barrierTypeLabel} that were not located on the aquatic network
        {customRank ? ', ' : ' and'} any that have been removed
        {customRank &&
          ', and any that you filtered out during your prioritization'}
        .
        {barrierType === 'small_barriers' &&
          '  These data only include road-related barriers that have been assessed for impacts to aquatic organisms.'}
      </Text>
    </Box>
  )
}

Options.propTypes = {
  barrierType: PropTypes.string.isRequired,
  options: PropTypes.shape({
    includeUnranked: PropTypes.bool,
  }).isRequired,
  customRank: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
}

Options.defaultProps = {
  customRank: false,
}

export default Options
