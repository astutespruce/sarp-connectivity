import React from 'react'
import PropTypes from 'prop-types'
import { View } from '@react-pdf/renderer'

import { pointLegends } from 'components/Summary/layers'
import { capitalize } from 'util/format'
import { barrierTypeLabels } from 'config'
import LegendElement from './elements/LegendElement'

export const getLegendEntries = ({ name, barrierType }) => {
  const barrierTypeLabel = barrierTypeLabels[barrierType]
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
      label: 'Upstream network',
      borderWidth: 2,
    },
    {
      color: '#1891ac',
      label: 'Stream reach',
      type: 'line',
      borderWidth: 2,
    },
    {
      color: '#9370db',
      label: 'Altered stream reach (canal / ditch)',
      type: 'line',
      borderWidth: 2,
    },
    {
      label: 'Intermittent / ephemeral stream reach',
      color: '#1891ac',
      type: 'line',
      borderStyle: 'dashed',
      borderWidth: 2,
    },
  ]
  const { primary, offnetwork, damsSecondary, waterfalls } = pointLegends
  entries.push({
    ...primary,
    type: 'circle',
    label: `${capitalize(
      barrierTypeLabel
    )} analyzed for impacts to aquatic connectivity`,
  })

  entries.push({
    ...offnetwork,
    type: 'circle',
    label: `${capitalize(
      barrierTypeLabel
    )} not analyzed for impacts to aquatic connectivity`,
  })

  if (barrierType === 'small_barriers') {
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
    <View
      style={{
        flex: `1 1 auto`,
      }}
    >
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
