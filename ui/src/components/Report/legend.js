import { pointLegends } from 'components/Summary/layers'
import { capitalize } from 'util/format'

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
      label: 'dams analyzed for impacts to aquatic connectivity',
    })
  }

  entries.push({
    ...waterfalls,
    type: 'circle',
    label: 'Waterfalls',
  })

  return entries
}
