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
import DataProviders from './DataProviders'

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
  DataProviders,
}

export const useRegionBounds = () => ({
  total: useSummaryData().bounds,
  ...Object.fromEntries(
    Object.entries(useRegionSummary()).map(([id, { bounds }]) => [id, bounds])
  ),
})
