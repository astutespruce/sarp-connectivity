import React, { useState } from 'react'
import { Box, Flex, Text, Spinner } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { useQueryClient } from '@tanstack/react-query'

import { useCrossfilter } from 'components/Crossfilter'
import { ToggleButton } from 'components/Button'
import { TopBar, mapConfig } from 'components/Map'
import {
  fetchBarrierInfo,
  fetchBarrierRanks,
  useBarrierType,
} from 'components/Data'
import { Sidebar } from 'components/Sidebar'
import BarrierDetails from 'components/BarrierDetails'
import { trackPrioritize } from 'util/analytics'

import Map from './Map'
import { unitLayerConfig } from './config'
import UnitChooser, { getSingularLabel } from './UnitChooser'
import LayerChooser from './LayerChooser'
import Filters from './Filters'
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
  const {
    state: { filters },
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
    bounds: mapConfig.bounds,
    zoom: null,
  })

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
      bounds: mapConfig.bounds,
    }))
  }

  const handleMapLoad = (map) => {
    setIsLoading(false)
    map.on('zoomend', () => {
      setState((prevState) => ({ ...prevState, zoom: map.getZoom() }))
    })
  }

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
  const handleSelectUnit = (unit) => {
    const { id } = unit

    setState(({ summaryUnits: prevSummaryUnits, ...prevState }) => {
      // NOTE: we are always creating a new object,
      // because we cannot mutate the underlying object
      // without causing the setSummaryUnits call to be a no-op
      const index = prevSummaryUnits.findIndex(
        ({ id: unitId }) => unitId === id
      )

      let nextSummaryUnits = prevSummaryUnits
      if (index === -1) {
        // add it
        nextSummaryUnits = prevSummaryUnits.concat([unit])
      } else {
        // remove it
        nextSummaryUnits = prevSummaryUnits
          .slice(0, index)
          .concat(prevSummaryUnits.slice(index + 1))
      }

      return {
        ...prevState,
        selectedBarrier: null,
        summaryUnits: nextSummaryUnits,
      }
    })
  }

  const loadBarrierInfo = async () => {
    setIsLoading(true)

    // only select units with non-zero ranked barriers
    let nonzeroSummaryUnits = []
    switch (barrierType) {
      case 'combined_barriers': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({ ranked_dams = 0, ranked_small_barriers = 0 }) =>
            ranked_dams + ranked_small_barriers > 0
        )
        break
      }
      case 'largefish_barriers': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({
            ranked_largefish_barriers_dams = 0,
            ranked_largefish_barriers_small_barriers = 0,
          }) =>
            ranked_largefish_barriers_dams +
              ranked_largefish_barriers_small_barriers >
            0
        )
        break
      }
      case 'smallfish_barriers': {
        nonzeroSummaryUnits = summaryUnits.filter(
          ({
            ranked_smallfish_barriers_dams = 0,
            ranked_smallfish_barriers_small_barriers = 0,
          }) =>
            ranked_smallfish_barriers_dams +
              ranked_smallfish_barriers_small_barriers >
            0
        )
        break
      }
      default: {
        // dams or small_barriers individually
        nonzeroSummaryUnits = summaryUnits.filter(
          ({ [`ranked_${barrierType}`]: count }) => count > 0
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
        fetchBarrierInfo(barrierType, layer, nonzeroSummaryUnits),

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
        fetchBarrierRanks(barrierType, layer, summaryUnits, filters),

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

  // WARNING: this is passed into map at construction type, any
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
              />
            )
          }
          break
        }
        case 'filter': {
          sidebarContent = (
            <Filters
              onBack={handleFilterBack}
              onSubmit={loadRankInfo}
              onStartOver={handleStartOver}
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
                layer,
                summaryUnits,
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
          Zoom in further to select a {getSingularLabel(layer)}
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
