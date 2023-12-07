import { useSummaryData } from './Summary'
import { useRegionSummary } from './RegionSummary'
import { useStateSummary } from './StateSummary'
import {
  fetchBarrierInfo,
  fetchBarrierRanks,
  getDownloadURL,
  searchBarriers,
} from './API'
import { Provider as BarrierTypeProvider, useBarrierType } from './BarrierType'

export {
  useSummaryData,
  useRegionSummary,
  useStateSummary,
  fetchBarrierInfo,
  fetchBarrierRanks,
  searchBarriers,
  BarrierTypeProvider,
  useBarrierType,
  getDownloadURL,
}

export const useRegionBounds = () => ({
  total: useSummaryData().bounds,
  ...Object.fromEntries(
    Object.entries(useRegionSummary()).map(([id, { bounds }]) => [id, bounds])
  ),
})
