import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import {
  DAM_CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  BARRIER_SEVERITY,
} from '../../../config/constants'

const Construction = ({
  barrierType,
  construction,
  purpose,
  condition,
  passagefacility,
  year,
  height,
  width,
  roadtype,
  crossingtype,
  severityclass,
}) => {
  if (barrierType === 'dams') {
    return (
      <Box>
        <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
          Construction information
        </Text>

        <Box as="ul" sx={{ mt: '0.5rem' }}>
          <li>Barrier type: dam</li>
          {year > 0 ? <li>Constructed completed: {year}</li> : null}
          {height > 0 ? <li>Height: {height} feet</li> : null}
          {width > 0 ? <li>Width: {width} feet</li> : null}
          {construction && CONSTRUCTION[construction] ? (
            <li>
              Construction material: {CONSTRUCTION[construction].toLowerCase()}
            </li>
          ) : null}
          {purpose && PURPOSE[purpose] ? (
            <li>Purpose: {PURPOSE[purpose].toLowerCase()}</li>
          ) : null}
          {condition && DAM_CONDITION[condition] ? (
            <li>
              Structural condition: {DAM_CONDITION[condition].toLowerCase()}
            </li>
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
  }

  return (
    <Box>
      <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>
        Construction information
      </Text>

      <Box as="ul" sx={{ mt: '0.5rem' }}>
        <li>Barrier type: road-related barrier</li>
        {roadtype ? <li>Road type: {roadtype}</li> : null}
        {crossingtype ? <li>Crossing type: {crossingtype}</li> : null}
        {condition ? <li>Condition: {condition}</li> : null}
        {severityclass !== null ? (
          <li>Severity: {BARRIER_SEVERITY[severityclass]}</li>
        ) : null}
      </Box>
    </Box>
  )
}

Construction.propTypes = {
  barrierType: PropTypes.string.isRequired,
  height: PropTypes.number,
  width: PropTypes.number,
  year: PropTypes.number,
  construction: PropTypes.number,
  purpose: PropTypes.number,
  condition: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  passagefacility: PropTypes.number,
  roadtype: PropTypes.string,
  crossingtype: PropTypes.string,
  severityclass: PropTypes.number,
}

Construction.defaultProps = {
  height: 0,
  width: 0,
  year: 0,
  construction: 0,
  purpose: 0,
  condition: 0,
  passagefacility: 0,
  roadtype: null,
  crossingtype: null,
  severityclass: null,
}

export default Construction
