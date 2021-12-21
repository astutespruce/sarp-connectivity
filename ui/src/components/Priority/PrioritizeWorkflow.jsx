import React, { useState, useCallback, useRef } from 'react'
import { Box, Flex, Text, Spinner } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { useCrossfilter } from 'components/Crossfilter'
import { ToggleButton } from 'components/Button'
import { TopBar } from 'components/Map'
import {
  fetchBarrierInfo,
  fetchBarrierRanks,
  useBarrierType,
} from 'components/Data'
import { Sidebar } from 'components/Sidebar'
import BarrierDetails from 'components/BarrierDetails'
import { trackPrioritize } from 'util/analytics'

import Map from './Map'
import UnitChooser from './UnitChooser'
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

  // individually-managed states
  const [isLoading, setIsLoading] = useState(true)
  const [isError, setIsError] = useState(false)
  const [bounds, setBounds] = useState(null)
  const [step, setStep] = useState('select')
  const stepRef = useRef(step) // need to keep a ref to use in callback below

  const [
    {
      selectedBarrier,
      searchFeature,
      layer,
      summaryUnits,
      rankData,
      scenario,
      resultsType,
      tierThreshold,
    },
    setState,
  ] = useState({
    selectedBarrier: null,
    searchFeature: null,
    layer: null,
    summaryUnits: [],
    rankData: [],
    scenario: 'ncwc',
    resultsType: 'full',
    tierThreshold: 1,
  })

  // keep the reference in sync
  stepRef.current = step

  const handleMapLoad = () => {
    setIsLoading(false)
  }

  const handleUnitChooserBack = () => {
    handleSetLayer(null)
  }

  const handleFilterBack = () => {
    setFilterData([])
    setStep('select')
  }

  const handleResultsBack = () => {
    setStep('filter')
    setState((prevState) => ({
      ...prevState,
      rankData: [],
      scenario: 'ncwc',
      resultsType: 'full',
      tierThreshold: 1,
    }))
  }

  const handleSearch = useCallback((nextSearchFeature) => {
    setState((prevState) => ({
      ...prevState,
      searchFeature: nextSearchFeature,
    }))
  }, [])

  const handleSetLayer = (nextLayer) => {
    setState((prevState) => ({
      ...prevState,
      searchFeature: null,
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
        searchFeature: null,
      }
    })
  }

  const loadBarrierInfo = () => {
    setIsLoading(true)

    const fetchData = async () => {
      const { csv, bounds: newBounds = null } = await fetchBarrierInfo(
        barrierType,
        layer,
        summaryUnits
      )

      if (csv) {
        setFilterData(csv)
        setStep('filter')
        if (newBounds !== null) {
          setBounds(newBounds.split(',').map(parseFloat))
        }
        setIsLoading(false)
      } else {
        setIsLoading(false)
        setIsError(true)
      }
    }
    fetchData()
  }

  const loadRankInfo = () => {
    setIsLoading(true)
    const fetchData = async () => {
      const { csv, bounds: newBounds } = await fetchBarrierRanks(
        barrierType,
        layer,
        summaryUnits,
        filters
      )

      if (csv) {
        setState((prevState) => ({
          ...prevState,
          rankData: csv,
        }))
        setStep('results')
        if (newBounds !== null) {
          setBounds(newBounds.split(',').map(parseFloat))
        }
        setIsLoading(false)
      } else {
        setIsLoading(false)
        setIsError(true)
      }
    }
    fetchData()
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
          }}
        >
          <Spinner size="2rem" sx={{ mr: '1rem' }} />
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
                setSearchFeature={handleSearch}
                onSubmit={loadBarrierInfo}
              />
            )
          }
          break
        }
        case 'filter': {
          sidebarContent = (
            <Filters onBack={handleFilterBack} onSubmit={loadRankInfo} />
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
          searchFeature={searchFeature}
          selectedBarrier={selectedBarrier}
          summaryUnits={summaryUnits}
          rankedBarriers={rankData}
          tierThreshold={tierThreshold}
          scenario={scenario}
          onSelectUnit={handleSelectUnit}
          onSelectBarrier={handleSelectBarrier}
          onMapLoad={handleMapLoad}
        />

        {step === 'results' && (
          <TopBar>
            <Text sx={{ mr: '0.5rem' }}>Show ranks for:</Text>
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
        )}
      </Box>
    </Flex>
  )
}

export default Prioritize
