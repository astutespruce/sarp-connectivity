import React from 'react'
import PropTypes from 'prop-types'

import { Checkbox } from 'components/Button'
import { HelpText } from 'components/Text'
import { Box } from 'components/Grid'
import styled from 'style'

const Wrapper = styled.div``

const Options = ({ barrierType, options, customRank, onChange }) => {
  const { unranked } = options

  const handleUnrankedChange = checked => {
    onChange({
      ...options,
      unranked: checked,
    })
  }

  return (
    <Wrapper>
      <Box>
        <Checkbox
          id="unranked"
          label={`Include unranked ${barrierType}?`}
          checked={unranked}
          onChange={handleUnrankedChange}
        />

        <HelpText mt="0.5rem" ml="2rem">
          This will include {barrierType} within your selected geographic area
          that were not prioritized in the analysis. These include any{' '}
          {barrierType} that were not located on the aquatic network
          {customRank && ' or that you filtered out during your prioritization'}
          .
          {barrierType === 'barriers' &&
            '  These data only include road-related barriers that have been assessed for impacts to aquatic organisms.'}
        </HelpText>
      </Box>
    </Wrapper>
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

export default Options
