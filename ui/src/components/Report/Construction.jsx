import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import {
  DAM_CONDITION,
  CONSTRUCTION,
  PASSAGEFACILITY,
  PURPOSE,
  BARRIER_SEVERITY,
} from '../../../config/constants'

import { List, ListItem } from './elements'

// TODO: expand to handle small barrier

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
      <List title="Construction information">
        <ListItem>
          <Text>Barrier type: dam</Text>
        </ListItem>
        {year > 0 ? (
          <ListItem>
            <Text>Constructed completed: {year}</Text>
          </ListItem>
        ) : null}
        {height > 0 ? (
          <ListItem>
            <Text>Height: {height} feet</Text>
          </ListItem>
        ) : null}
        {width > 0 ? (
          <ListItem>
            <Text>Width: {width} feet</Text>
          </ListItem>
        ) : null}
        {construction && CONSTRUCTION[construction] ? (
          <ListItem>
            <Text>
              Construction material: {CONSTRUCTION[construction].toLowerCase()}
            </Text>
          </ListItem>
        ) : null}
        {purpose && PURPOSE[purpose] ? (
          <ListItem>
            <Text>Purpose: {PURPOSE[purpose].toLowerCase()}</Text>
          </ListItem>
        ) : null}
        {condition && DAM_CONDITION[condition] ? (
          <ListItem>
            <Text>
              Structural condition: {DAM_CONDITION[condition].toLowerCase()}
            </Text>
          </ListItem>
        ) : null}

        {PASSAGEFACILITY[passagefacility] ? (
          <ListItem>
            <Text>
              Passage facility type:{' '}
              {PASSAGEFACILITY[passagefacility].toLowerCase()}
            </Text>
          </ListItem>
        ) : null}
      </List>
    )
  }

  return (
    <List title="Construction information">
      <ListItem>
        <Text>Barrier type: road-related barrier</Text>
      </ListItem>

      {roadtype ? (
        <ListItem>
          <Text>Road type: {roadtype}</Text>
        </ListItem>
      ) : null}
      {crossingtype ? (
        <ListItem>
          <Text>Crossing type: {crossingtype}</Text>
        </ListItem>
      ) : null}

      {condition ? (
        <ListItem>
          <Text>Condition: {condition}</Text>
        </ListItem>
      ) : null}

      {severityclass !== null ? (
        <ListItem>
          <Text>Severity: {BARRIER_SEVERITY[severityclass]}</Text>
        </ListItem>
      ) : null}
    </List>
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
