import { YEAR_REMOVED_BINS } from 'config'

const unpackYearRemoved = (text) => {
  if (!text) {
    return Object.keys(YEAR_REMOVED_BINS).map(() => ({
      count: 0,
      gainmiles: 0,
    }))
  }

  return text.split(',').map((part) => {
    if (!part) {
      return { count: 0, gainmiles: 0 }
    }
    const [count = '0', gainmiles = '0'] = part.split('|')
    return { count: parseFloat(count), gainmiles: parseFloat(gainmiles) }
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
      const { count: dams = 0, gainmiles: damsGainMiles = 0 } =
        removedDamsByYear[bin]
      const {
        count: smallBarriers = 0,
        gainmiles: smallBarriersGainMiles = 0,
      } = removedSmallBarriersByYear[bin]
      return {
        label,
        dams,
        damsGainMiles,
        smallBarriers,
        smallBarriersGainMiles,
      }
    })
    .reverse()
}
