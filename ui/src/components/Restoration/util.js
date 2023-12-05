import { YEAR_REMOVED_BINS } from 'config'
import { isEmptyString } from 'util/string'

const unpackYearRemoved = (text) => {
  if (isEmptyString(text)) {
    return Object.keys(YEAR_REMOVED_BINS).map(() => ({
      count: 0,
      countNoNetwork: 0,
      gainmiles: 0,
    }))
  }

  return text.split(',').map((part) => {
    if (!part) {
      return { count: 0, gainmiles: 0 }
    }
    const [rawCount = '0', gainmiles = '0'] = part.split('|')
    const [count, countNoNetwork] = rawCount.split('/')
    return {
      count: parseFloat(count),
      countNoNetwork:
        countNoNetwork !== undefined ? parseFloat(countNoNetwork) : 0,
      gainmiles: parseFloat(gainmiles),
    }
  })
}

export const extractYearRemovedStats = (
  removedDamsByYearText,
  removedSmallBarriersByYearText
) => {
  const removedDamsByYear = unpackYearRemoved(removedDamsByYearText)
  const removedSmallBarriersByYear = unpackYearRemoved(
    removedSmallBarriersByYearText
  )

  return Object.entries(YEAR_REMOVED_BINS)
    .map(([bin, label]) => {
      const {
        count: dams = 0,
        countNoNetwork: damsNoNetwork = 0,
        gainmiles: damsGainMiles = 0,
      } = removedDamsByYear[bin]
      const {
        count: smallBarriers = 0,
        countNoNetwork: smallBarriersNoNetwork = 0,
        gainmiles: smallBarriersGainMiles = 0,
      } = removedSmallBarriersByYear[bin]
      return {
        label,
        dams,
        damsNoNetwork,
        damsGainMiles,
        smallBarriers,
        smallBarriersNoNetwork,
        smallBarriersGainMiles,
      }
    })
    .reverse()
}
