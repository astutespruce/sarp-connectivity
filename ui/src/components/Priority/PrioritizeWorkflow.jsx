import React, { useCallback, useState, useRef } from 'react'
import { Box, Flex, Text, Spinner } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { useQueryClient } from '@tanstack/react-query'

import { getSingularUnitLabel, barrierTypeLabels } from 'config'
import BarrierDetails from 'components/BarrierDetails'
import { ToggleButton } from 'components/Button'
import { useCrossfilter } from 'components/Crossfilter'
import { TopBar } from 'components/Map'
import {
  fetchBarrierInfo,
  fetchBarrierRanks,
  useBarrierType,
  useSummaryData,
  fetchUnitDetails,
} from 'components/Data'
import { Sidebar } from 'components/Sidebar'
import {
  Filters,
  LayerChooser,
  UnitChooser,
  unitLayerConfig,
  SubmitButton,
} from 'components/Workflow'
import { trackPrioritize } from 'util/analytics'

import Map from './Map'
import Results from './Results'

const scenarioOptions = [
  { value: 'nc', label: 'network connectivity' },
  { value: 'wc', label: 'watershed condition' },
  { value: 'ncwc', label: 'combined' },
]

const resultTypeOptions = [
  {
    value: 'full',
    label: 'full networks',
  },
  {
    value: 'perennial',
    label: 'perennial reaches only',
  },
]

const Prioritize = () => {
  const barrierType = useBarrierType()
  const barrierTypeLabel = barrierTypeLabels[barrierType]
  const { bounds: fullBounds } = useSummaryData()
  const {
    state: { filters, filteredCount },
    setData: setFilterData,
  } = useCrossfilter()
  const queryClient = useQueryClient()

  // individually-managed states
  const [isLoading, setIsLoading] = useState(true)
  const [isError, setIsError] = useState(false)

  const [
    {
      step,
      selectedBarrier,
      layer,
      summaryUnits,
      rankData,
      scenario,
      resultsType,
      tierThreshold,
      bounds,
      zoom,
    },
    setState,
  ] = useState({
    step: 'select',
    selectedBarrier: null,
    layer: null,
    summaryUnits: [],
    rankData: [],
    scenario: 'ncwc',
    resultsType: 'full',
    tierThreshold: 1,
    bounds: fullBounds,
    zoom: null,
  })

  const summaryUnitsRef = useRef(new Set())

  const mapRef = useRef(null)

  const handleStartOver = () => {
    setFilterData(null)
    setState(() => ({
      step: 'select',
      selectedBarrier: null,
      layer: null,
      summaryUnits: [],
      rankData: [],
      scenario: 'ncwc',
      resultsType: 'full',
      tierThreshold: 1,
      bounds: fullBounds,
    }))
  }

  const handleMapLoad = (map) => {
    mapRef.current = map
    setIsLoading(false)
    map.on('zoomend', () => {
      setState((prevState) => ({ ...prevState, zoom: map.getZoom() }))
    })
  }

  const handleZoomBounds = useCallback((newBounds) => {
    const { current: map } = mapRef

    if (!(map && newBounds)) return

    map.fitBounds(newBounds, { padding: 100 })
  }, [])

  const handleUnitChooserBack = () => {
    handleSetLayer(null)
  }

  const handleFilterBack = () => {
    setFilterData(null)
    setState((prevState) => ({ ...prevState, step: 'select' }))
  }

  const handleResultsBack = () => {
    setState((prevState) => ({
      ...prevState,
      step: 'filter',
      rankData: [],
      scenario: 'ncwc',
      resultsType: 'full',
      tierThreshold: 1,
    }))
  }

  const handleSetLayer = (nextLayer) => {
    setState((prevState) => ({
      ...prevState,
      summaryUnits: [],
      layer: nextLayer,
    }))
  }

  // Toggle selected unit in or out of selection
  const handleSelectUnit = ({
    layer: selectedUnitLayer,
    id,
    ...preFetchedUnitData
  }) => {
    if (summaryUnitsRef.current.has(id)) {
      // remove it
      summaryUnitsRef.current.delete(id)
      setState((prevState) => ({
        ...prevState,
        isUnitError: false,
        isUnitLoading: false,
        summaryUnits: prevState.summaryUnits.filter(
          ({ id: unitId }) => unitId !== id
        ),
      }))
      return
    }

    // add it
    // assume if unitData are present it was from a search feature and already
    // has necessary data loaded
    if (Object.keys(preFetchedUnitData).length > 0) {
      summaryUnitsRef.current.add(id)
      setState((prevState) => ({
        ...prevState,
        isUnitError: false,
        isUnitLoading: false,
        summaryUnits: prevState.summaryUnits.concat([
          {
            layer: selectedUnitLayer,
            id,
            ...preFetchedUnitData,
            bbox: preFetchedUnitData.bbox
              ? preFetchedUnitData.bbox.split(',').map(parseFloat)
              : null,
          },
        ]),
      }))
      return
    }

    queryClient
      .fetchQuery({
        queryKey: [selectedUnitLayer, id],
        queryFn: async () => fetchUnitDetails(selectedUnitLayer, id),
      })
      .then((unitData) => {
        if (summaryUnitsRef.current.has(id)) {
          // if multiple requests resolved with this id due to slow requests
          setState((prevState) => ({
            ...prevState,
            isUnitError: false,
            isUnitLoading: false,
          }))
          return
        }

        summaryUnitsRef.current.add(id)
        setState((prevState) => ({
          ...prevState,
          isUnitError: false,
          isUnitLoading: false,
          summaryUnits: prevState.summaryUnits.concat([unitData]),
        }))
      })
      .catch(() => {
        setState((prevState) => ({
          ...prevState,
          isUnitError: true,
          isUnitLoading: false,
        }))
      })
  }

  const loadBarrierInfo = async () => {
    setIsLoading(true)

    // only select units with non-zero ranked barriers
    let nonzeroSummaryUnits = []
    /* eslint-disable default-case */
    switch (barrierType) {
      case 'dams': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({ rankedDams }) => rankedDams > 0
        )
        break
      }
      case 'small_barriers': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({ rankedSmallBarriers }) => rankedSmallBarriers > 0
        )
        break
      }
      case 'combined_barriers': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({ rankedDams = 0, rankedSmallBarriers = 0 }) =>
            rankedDams + rankedSmallBarriers > 0
        )
        break
      }
      case 'largefish_barriers': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({
            rankedLargefishBarriersDams = 0,
            rankedLargefishBarriersSmallBarriers = 0,
          }) =>
            rankedLargefishBarriersDams + rankedLargefishBarriersSmallBarriers >
            0
        )
        break
      }
      case 'smallfish_barriers': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({
            rankedSmallfishBarriersDams = 0,
            rankedSmallfishBarriersSmallBarriers = 0,
          }) =>
            rankedSmallfishBarriersDams + rankedSmallfishBarriersSmallBarriers >
            0
        )
        break
      }
    }

    const {
      error,
      data,
      bounds: newBounds = null,
    } = await queryClient.fetchQuery({
      queryKey: [barrierType, layer, nonzeroSummaryUnits],
      queryFn: async () =>
        fetchBarrierInfo(barrierType, {
          [layer]: nonzeroSummaryUnits.map(({ id }) => id),
        }),

      staleTime: 30 * 60 * 1000, // 30 minutes
      // staleTime: 1, // use then reload to force refresh of underlying data during dev
      refetchOnMount: false,
    })

    if (error || !data) {
      setIsLoading(false)
      setIsError(true)
      return
    }

    setFilterData(data)
    setState(({ bounds: prevBounds, ...prevState }) => ({
      ...prevState,
      step: 'filter',
      bounds: newBounds ? newBounds.split(',').map(parseFloat) : prevBounds,
      summaryUnits: nonzeroSummaryUnits,
    }))
    setIsLoading(false)
  }

  const loadRankInfo = async () => {
    setIsLoading(true)

    const {
      error,
      data,
      bounds: newBounds = null,
    } = await queryClient.fetchQuery({
      queryKey: [barrierType, layer, summaryUnits, filters],
      queryFn: async () =>
        fetchBarrierRanks(
          barrierType,
          { [layer]: summaryUnits.map(({ id }) => id) },
          filters
        ),

      staleTime: 30 * 60 * 1000, // 30 minutes
      // staleTime: 1, // use then reload to force refresh of underlying data during dev
      refetchOnMount: false,
    })

    if (error || !data) {
      setIsLoading(false)
      setIsError(true)
    }

    setState(({ bounds: prevBounds, ...prevState }) => ({
      ...prevState,
      step: 'results',
      rankData: data,
      bounds: newBounds ? newBounds.split(',').map(parseFloat) : prevBounds,
    }))
    setIsLoading(false)
  }

  const handleSetScenario = (nextScenario) => {
    setState((prevState) => ({ ...prevState, scenario: nextScenario }))
  }

  const handleSetResultsType = (nextResultsType) => {
    setState((prevState) => ({
      ...prevState,
      resultsType: nextResultsType,
    }))
  }

  const handleSetTierThreshold = (newThreshold) => {
    setState((prevState) => ({ ...prevState, tierThreshold: newThreshold }))
  }

  // WARNING: this is passed into map at construction time, any
  // local state referenced here is not updated when the callback
  // is later called.  To get around that, use reference to step instead.
  const handleSelectBarrier = (feature) => {
    setState((prevState) => ({
      ...prevState,
      selectedBarrier: feature,
    }))
  }

  const handleDetailsClose = () => {
    setState((prevState) => ({
      ...prevState,
      selectedBarrier: null,
    }))
  }

  let sidebarContent = null

  if (selectedBarrier === null) {
    if (isError) {
      sidebarContent = (
        <Flex
          sx={{
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            p: '1rem',
            flex: '1 1 auto',
            height: '100%',
          }}
        >
          <Flex sx={{ color: 'highlight', alignItems: 'center' }}>
            <ExclamationTriangle size="2em" />
            <Text sx={{ ml: '0.5rem', fontSize: '2rem' }}>Whoops!</Text>
          </Flex>
          There was an error loading these data. Please refresh your browser
          page and try again.
          <Text variant="help" sx={{ mt: '2rem' }}>
            If it happens again, please{' '}
            <a href="mailto:kat@southeastaquatics.net">contact us</a>.
          </Text>
        </Flex>
      )
    } else if (isLoading) {
      sidebarContent = (
        <Flex
          sx={{
            flex: '1 1 auto',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            gap: '1rem',
          }}
        >
          <Spinner size="2rem" />
          <Text>Loading...</Text>
        </Flex>
      )
    } else {
      switch (step) {
        case 'select': {
          if (layer === null) {
            sidebarContent = <LayerChooser setLayer={handleSetLayer} />
          } else {
            sidebarContent = (
              <UnitChooser
                layer={layer}
                summaryUnits={summaryUnits}
                onBack={handleUnitChooserBack}
                selectUnit={handleSelectUnit}
                onSubmit={loadBarrierInfo}
                onStartOver={handleStartOver}
                onZoomBounds={handleZoomBounds}
              />
            )
          }
          break
        }
        case 'filter': {
          sidebarContent = (
            <Filters
              onBack={handleFilterBack}
              onStartOver={handleStartOver}
              SubmitButton={
                <SubmitButton
                  disabled={filteredCount === 0}
                  onClick={loadRankInfo}
                  label="Prioritize selected barriers"
                  title={
                    filteredCount === 0
                      ? `No ${barrierTypeLabel} selected for prioritization`
                      : null
                  }
                />
              }
            />
          )
          break
        }
        case 'results': {
          sidebarContent = (
            <Results
              rankData={rankData}
              tierThreshold={tierThreshold}
              scenario={scenario}
              resultsType={resultsType}
              config={{
                summaryUnits: { [layer]: summaryUnits.map(({ id }) => id) },
                filters,
                scenario,
              }}
              onSetTierThreshold={handleSetTierThreshold}
              onStartOver={handleStartOver}
              onBack={handleResultsBack}
            />
          )

          trackPrioritize({
            barrierType,
            unitType: layer,
            details: `ids: [${
              summaryUnits ? summaryUnits.map(({ id }) => id) : 'none'
            }], filters: ${
              filters ? Object.keys(filters) : 'none'
            }, scenario: ${scenario}`,
          })

          break
        }
        default: {
          sidebarContent = null
        }
      }
    }
  }

  let topbarContent = null
  if (step === 'results') {
    topbarContent = (
      <TopBar>
        <Text sx={{ mr: '0.5rem' }}>Show:</Text>
        <ToggleButton
          value={scenario}
          options={scenarioOptions}
          onChange={handleSetScenario}
        />
        <Text sx={{ mx: '0.5rem' }}>for</Text>
        <ToggleButton
          value={resultsType}
          options={resultTypeOptions}
          onChange={handleSetResultsType}
        />
      </TopBar>
    )
  } else if (
    step === 'select' &&
    layer !== null &&
    zoom < unitLayerConfig[layer].minzoom
  ) {
    topbarContent = (
      <TopBar>
        <Box sx={{ color: 'highlight', mt: '-3px' }}>
          <ExclamationTriangle size="1.25em" />
        </Box>
        <Text sx={{ ml: '0.5rem', color: 'highlight' }}>
          Zoom in further to select a {getSingularUnitLabel(layer)}
        </Text>
      </TopBar>
    )
  }

  return (
    <Flex sx={{ height: '100%' }}>
      <Sidebar>
        {selectedBarrier !== null ? (
          <BarrierDetails
            barrier={selectedBarrier}
            onClose={handleDetailsClose}
          />
        ) : (
          sidebarContent
        )}
      </Sidebar>

      <Box sx={{ position: 'relative', flex: '1 0 auto', height: '100%' }}>
        <Map
          bounds={bounds}
          allowUnitSelect={step === 'select'}
          activeLayer={layer}
          selectedBarrier={selectedBarrier}
          summaryUnits={summaryUnits}
          rankedBarriers={rankData}
          tierThreshold={tierThreshold}
          resultsType={resultsType}
          scenario={(resultsType === 'perennial' ? 'p' : '') + scenario}
          onSelectUnit={handleSelectUnit}
          onSelectBarrier={handleSelectBarrier}
          onMapLoad={handleMapLoad}
        >
          {topbarContent}
        </Map>
      </Box>
    </Flex>
  )
}

export default Prioritize
