import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import {
  DAM_CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
} from '../../../config/constants'

// TODO: expand to handle small barrier

const Construction = ({
  construction,
  purpose,
  condition,
  passagefacility,
  year,
  height,
}) => (
  <Box>
    <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
      Construction information
    </Text>

    <Box as="ul" sx={{ mt: '0.5rem' }}>
      <li>Barrier type: dam</li>
      {year > 0 ? <li>Constructed completed: {year}</li> : null}
      {height > 0 ? <li>Height: {height} feet</li> : null}
      {construction && CONSTRUCTION[construction] ? (
        <li>
          Construction material: {CONSTRUCTION[construction].toLowerCase()}
        </li>
      ) : null}
      {purpose && PURPOSE[purpose] ? (
        <li>Purpose: {PURPOSE[purpose].toLowerCase()}</li>
      ) : null}
      {condition && DAM_CONDITION[condition] ? (
        <li>Structural condition: {DAM_CONDITION[condition].toLowerCase()}</li>
      ) : null}

      {PASSAGEFACILITY[passagefacility] ? (
        <li>
          Passage facility type:{' '}
          {PASSAGEFACILITY[passagefacility].toLowerCase()}
        </li>
      ) : null}
    </Box>
  </Box>
)

Construction.propTypes = {
  height: PropTypes.number,
  year: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.number,
  passagefacility: PropTypes.number,
}

Construction.defaultProps = {
  height: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
}

export default Construction
