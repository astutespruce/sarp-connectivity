import React from 'react'
import PropTypes from 'prop-types'
import { Box, Paragraph } from 'theme-ui'

import { Checkbox } from 'components/Button'

const Options = ({ barrierType, options, customRank, onChange }) => {
  const { unranked } = options

  const handleUnrankedChange = () => {
    onChange({
      ...options,
      unranked: !unranked,
    })
  }

  return (
    <Box sx={{ alignItems: 'flex-start', mt: '1rem' }}>
      <Checkbox
        id="unranked"
        label={`Include unranked ${barrierType}?`}
        checked={unranked}
        onChange={handleUnrankedChange}
        sx={{
          fontWeight: 'bold',
          fontSize: 3,
        }}
      />

      <Paragraph sx={{ color: 'grey.7', mt: '1rem' }}>
        This will include {barrierType} within your selected geographic area
        that were not prioritized in the analysis. These include any{' '}
        {barrierType} that were not located on the aquatic network
        {customRank && ' or that you filtered out during your prioritization'}.
        {barrierType === 'barriers' &&
          '  These data only include road-related barriers that have been assessed for impacts to aquatic organisms.'}
      </Paragraph>
    </Box>
  )
}

Options.propTypes = {
  barrierType: PropTypes.string.isRequired,
  options: PropTypes.shape({
    unranked: PropTypes.bool,
  }).isRequired,
  customRank: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
}

Options.defaultProps = {
  customRank: false,
}

export default Options
