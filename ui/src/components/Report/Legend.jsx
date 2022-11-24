import React from 'react'
import PropTypes from 'prop-types'
import { View } from '@react-pdf/renderer'

import { pointLegends } from 'components/Summary/layers'
import { capitalize } from 'util/format'
import { barrierTypeLabels } from 'config'
import LegendElement from './elements/LegendElement'

const flowlineSymbols = {
  flowline: {
    color: '#1891ac',
    label: 'Stream reach',
    type: 'line',
    borderWidth: 2,
  },
  alteredFlowline: {
    color: '#9370db',
    label: 'Altered stream reach (canal / ditch)',
    type: 'line',
    borderWidth: 2,
  },
  intermittentFlowline: {
    label: 'Intermittent / ephemeral stream reach',
    color: '#1891ac',
    type: 'line',
    borderStyle: 'dashed',
    borderWidth: 2,
  },
}

export const getLegendEntries = ({ name, barrierType, visibleLayers }) => {
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

  if (visibleLayers) {
    if (
      barrierType === 'small_barriers' &&
      visibleLayers.has('dams-secondary')
    ) {
      entries.push({
        ...damsSecondary,
        type: 'circle',
        label: 'Dams analyzed for impacts to aquatic connectivity',
      })
    }

    const flowlineElements = Object.entries(flowlineSymbols)
      .filter(([key, _]) => visibleLayers.has(key))
      .map(([_, symbol]) => symbol)
    entries.push(...flowlineElements)

    if (visibleLayers.has('waterfalls')) {
      entries.push({
        ...waterfalls,
        type: 'circle',
        label: 'Waterfalls',
      })
    }
  } else {
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

    entries.push(...Object.values(flowlineSymbols))
  }

  return entries
}

const Legend = ({ barrierType, name, visibleLayers }) => {
  const entries = getLegendEntries({ barrierType, name, visibleLayers })

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
  visibleLayers: PropTypes.object, // Set()
}

Legend.defaultProps = {
  visibleLayers: null,
}

export default Legend
