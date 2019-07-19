import React, { useState, useCallback, useRef } from 'react'

import { useCrossfilter } from 'components/Crossfilter'
import { HelpText } from 'components/Text'
import { Flex } from 'components/Grid'
import { TopBar, TopBarToggle } from 'components/Map'
import {
  fetchBarrierInfo,
  fetchBarrierRanks,
  useBarrierType,
  getDownloadURL,
} from 'components/Data'
import Sidebar, { LoadingSpinner, ErrorMessage } from 'components/Sidebar'
import BarrierDetails from 'components/BarrierDetails'
import styled from 'style'

import { set } from 'immutable'
import Map from './Map'
import UnitChooser from './UnitChooser'
import LayerChooser from './LayerChooser'
import Filters from './Filters'
import Results from './Results'

const Wrapper = styled(Flex)`
  height: 100%;
`

const MapContainer = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
`

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

  const handleSearch = useCallback(nextSearchFeature => {
    setSearchFeature(nextSearchFeature)
  }, [])

  const handleSetLayer = nextLayer => {
    setSearchFeature(null)
    setSummaryUnits([])
    setLayer(nextLayer)
  }

  // Toggle selected unit in or out of selection
  const handleSelectUnit = unit => {
    const { id } = unit

    setSummaryUnits(prevSummaryUnits => {
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

  const handleSetScenario = nextScenario => {
    setScenario(nextScenario)
  }

  const handleSetTierThreshold = newThreshold => {
    setTierThreshold(newThreshold)
  }

  // WARNING: this is passed into map at construction type, any
  // local state referenced here is not updated when the callback
  // is later called.  To get around that, use reference to step instead.
  const handleSelectBarrier = feature => {
    const { current: curStep } = stepRef
    // don't show details when selecting units
    if (curStep === 'select') return

    // console.log('selected feature', feature)
    setSelectedBarrier(feature)
  }

  const handleDetailsClose = () => {
    setSelectedBarrier(null)
  }

  let sidebarContent = null

  if (selectedBarrier === null) {
    if (isError) {
      sidebarContent = (
        <ErrorMessage>
          There was an error loading these data. Please refresh your browser
          page and try again.
          <HelpText fontSize="1rem" mt="2rem">
            If it happens again, please{' '}
            <a href="mailto:kat@southeastaquatics.net">contact us</a>.
          </HelpText>
        </ErrorMessage>
      )
    } else if (isLoading) {
      sidebarContent = <LoadingSpinner />
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
              downloadURL={getDownloadURL(
                barrierType,
                layer,
                summaryUnits,
                filters
              )}
              onSetTierThreshold={handleSetTierThreshold}
              onBack={handleResultsBack}
            />
          )
          break
        }
        default: {
          sidebarContent = null
        }
      }
    }
  }

  return (
    <Wrapper>
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

      <MapContainer>
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
            Show ranks for:
            <TopBarToggle
              value={scenario}
              options={scenarioOptions}
              onChange={handleSetScenario}
            />
          </TopBar>
        )}
      </MapContainer>
    </Wrapper>
  )
}

export default Prioritize
