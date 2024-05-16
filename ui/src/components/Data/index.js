import { useSummaryData } from './Summary'
import { useRegionSummary } from './RegionSummary'
import {
  fetchBarrierInfo,
  fetchBarrierRanks,
  getDownloadURL,
  searchBarriers,
  fetchUnitDetails,
  fetchUnitList,
} from './API'
import { Provider as BarrierTypeProvider, useBarrierType } from './BarrierType'
import DataProviders from './DataProviders'

export {
  useSummaryData,
  useRegionSummary,
  fetchBarrierInfo,
  fetchBarrierRanks,
  searchBarriers,
  fetchUnitDetails,
  fetchUnitList,
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
