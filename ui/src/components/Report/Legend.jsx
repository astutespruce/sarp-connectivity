import React from 'react'
import PropTypes from 'prop-types'
import { View } from '@react-pdf/renderer'

import { capitalize } from 'util/format'
import { barrierTypeLabels, pointLegends } from 'config'
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
    label: 'Altered stream reach (canal / ditch / reservoir)',
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

export const getLegendEntries = ({ name, networkType, visibleLayers }) => {
  const networkTypeLabel = barrierTypeLabels[networkType]
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

  const { included: primary, unrankedBarriers, other } = pointLegends
  entries.push({
    ...primary.getSymbol(networkType),
    type: 'circle',
    label: capitalize(primary.getLabel(networkTypeLabel)),
  })

  unrankedBarriers
    .filter(
      ({ id }) =>
        // don't show minor barriers for dams view
        id !== 'minorBarrier' || networkType !== 'dams'
    )
    .forEach(({ getSymbol, getLabel }) => {
      entries.push({
        ...getSymbol(networkType),
        type: 'circle',
        label: capitalize(getLabel(networkTypeLabel)),
      })
    })

  other.forEach(({ id, getLabel, getSymbol }) => {
    // if visible layers are tracked, but not currently
    // visible, don't add to legend
    if (
      (id === 'dams-secondary' || id === 'waterfalls') &&
      visibleLayers &&
      !visibleLayers.has(id)
    ) {
      return
    }

    if (id === 'dams-secondary' && networkType !== 'small_barriers') {
      return
    }

    entries.push({
      ...getSymbol(networkType),
      type: 'circle',
      label: capitalize(getLabel(networkTypeLabel)),
    })
  })

  if (visibleLayers) {
    const flowlineElements = Object.entries(flowlineSymbols)
      .filter(([key, _]) => visibleLayers.has(key))
      .map(([_, symbol]) => symbol)
    entries.push(...flowlineElements)
  } else {
    entries.push(...Object.values(flowlineSymbols))
  }

  return entries
}

const Legend = ({ networkType, name, visibleLayers }) => {
  const entries = getLegendEntries({ networkType, name, visibleLayers })

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
  networkType: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  visibleLayers: PropTypes.object, // Set()
}

Legend.defaultProps = {
  visibleLayers: null,
}

export default Legend
