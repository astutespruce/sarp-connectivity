import React from 'react'
import PropTypes from 'prop-types'
import { View } from '@react-pdf/renderer'

import { pointLegends } from 'components/Summary/layers'
import { capitalize } from 'util/format'
import LegendElement from './elements/LegendElement'

export const getLegendEntries = ({ name, barrierType }) => {
  const entries = [
    {
      color: '#fd8d3c',
      borderColor: '#f03b20',
      type: 'circle',
      label: name,
      borderWidth: 2,
    },
    {
      color: '#fd8d3c',
      type: 'line',
      label: `Upstream network from ${name}`,
      borderWidth: 2,
    },
  ]
  const { primary, background, damsSecondary, waterfalls } = pointLegends
  entries.push({
    ...primary,
    type: 'circle',
    label: `${capitalize(
      barrierType
    )} analyzed for impacts to aquatic connectivity`,
  })

  entries.push({
    ...background,
    type: 'circle',
    label: `${capitalize(
      barrierType
    )} not analyzed for impacts to aquatic connectivity`,
  })

  if (barrierType === 'barriers') {
    entries.push({
      ...damsSecondary,
      type: 'circle',
      label: 'Dams analyzed for impacts to aquatic connectivity',
    })
  }

  entries.push({
    ...waterfalls,
    type: 'circle',
    label: 'Waterfalls',
  })

  return entries
}

const Legend = ({ barrierType, name }) => {
  const entries = getLegendEntries({ barrierType, name })

  return (
    <View>
      {entries.map((entry) => (
        <LegendElement key={entry.label} {...entry} />
      ))}
    </View>
  )
}

Legend.propTypes = {
  barrierType: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
}

export default Legend
