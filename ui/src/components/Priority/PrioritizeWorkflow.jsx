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

const Prioritize = () => {
  const barrierType = useBarrierType()
  const {
    state: { filters },
    setData: setFilterData,
  } = useCrossfilter()
  const [selectedBarrier, setSelectedBarrier] = useState(null)
  const [searchFeature, setSearchFeature] = useState(null)
  const [layer, setLayer] = useState(null)
  const [summaryUnits, setSummaryUnits] = useState([])
  const [rankData, setRankData] = useState([])
  const [scenario, setScenario] = useState('ncwc')
  const [tierThreshold, setTierThreshold] = useState(1)
  const [step, setStep] = useState('select')
  const stepRef = useRef(step) // need to keep a ref to use in callback below

  const [isLoading, setIsLoading] = useState(true)
  const [isError, setIsError] = useState(false)

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
    setRankData([])
    setTierThreshold(1)
    setScenario('ncwc')
  }

  const handleSearch = useCallback((nextSearchFeature) => {
    setSearchFeature(nextSearchFeature)
  }, [])

  const handleSetLayer = (nextLayer) => {
    setSearchFeature(null)
    setSummaryUnits([])
    setLayer(nextLayer)
  }

  // Toggle selected unit in or out of selection
  const handleSelectUnit = (unit) => {
    const { id } = unit

    setSummaryUnits((prevSummaryUnits) => {
      // NOTE: we are always creating a new object,
      // because we cannot mutate the underlying object
      // without causing the setSummaryUnits call to be a no-op
      const index = prevSummaryUnits.findIndex(
        ({ id: unitId }) => unitId === id
      )

      if (index === -1) {
        // add it
        return prevSummaryUnits.concat([unit])
      }

      // remove it
      return prevSummaryUnits
        .slice(0, index)
        .concat(prevSummaryUnits.slice(index + 1))
    })

    setSearchFeature(null)
  }

  const loadBarrierInfo = () => {
    setIsLoading(true)

    const fetchData = async () => {
      const { csv } = await fetchBarrierInfo(barrierType, layer, summaryUnits)

      if (csv) {
        setFilterData(csv)
        setStep('filter')
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
      const { csv } = await fetchBarrierRanks(
        barrierType,
        layer,
        summaryUnits,
        filters
      )

      if (csv) {
        setRankData(csv)
        setStep('results')
        setIsLoading(false)
      } else {
        setIsLoading(false)
        setIsError(true)
      }
    }
    fetchData()
  }

  const handleSetScenario = (nextScenario) => {
    setScenario(nextScenario)
  }

  const handleSetTierThreshold = (newThreshold) => {
    setTierThreshold(newThreshold)
  }

  // WARNING: this is passed into map at construction type, any
  // local state referenced here is not updated when the callback
  // is later called.  To get around that, use reference to step instead.
  const handleSelectBarrier = (feature) => {
    const { current: curStep } = stepRef
    // don't show details when selecting units
    if (curStep === 'select') return

    setSelectedBarrier(feature)
  }

  const handleDetailsClose = () => {
    setSelectedBarrier(null)
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
          </TopBar>
        )}
      </Box>
    </Flex>
  )
}

export default Prioritize
