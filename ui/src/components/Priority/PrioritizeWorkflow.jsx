import React, { useState, useCallback } from 'react'
import PropTypes from 'prop-types'

import { Flex, Box } from 'components/Grid'
import Sidebar from 'components/Sidebar'
import BarrierDetails from 'components/BarrierDetails'
import styled from 'style'

import Map from './Map'
import UnitChooser from './UnitChooser'
import LayerChooser from './LayerChooser'

const Wrapper = styled(Flex)`
  height: 100%;
`

const MapContainer = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
`

const Prioritize = ({ barrierType }) => {
  const [selectedBarrier, setSelectedBarrier] = useState({
    id: 90124,
    lat: 35.23275,
    lon: -94.601814,
    sarpid: 105413,
    source: 'NHDplus High Resolution watebodies instersecting *',
    name: 'null',
    countyname: 'Le Flore',
    State: 'Oklahoma',
    basin: 'Robert S. Kerr Reservoir',
    rarespp: 0,
    river: 'null',
    streamorder: 1,
    protectedland: false,
    HUC6: '111101',
    HUC8: '11110104',
    HUC12: '111101040603',
    ECO3: '8.4.7',
    ECO4: '37d',
    height: 0,
    year: 0,
    construction: 0,
    purpose: 0,
    condition: 0,
    recon: 0,
    feasibility: 0,
    gainmiles: 0.61,
    upstreammiles: 0.61,
    downstreammiles: 1.67,
    totalnetworkmiles: 2.28,
    landcover: 45,
    sizeclasses: 0,
    County: '40079',
    heightclass: 0,
    raresppclass: 0,
    gainmilesclass: 0,
    sinuosity: 1,
    landcoverclass: 0,
    streamorderclass: 1,
    se_nc_tier: 20,
    se_wc_tier: 14,
    se_ncwc_tier: 17,
    state_nc_tier: 17,
    state_wc_tier: 12,
    state_ncwc_tier: 15,
    hasnetwork: true,
  }) // FIXME
  const [searchFeature, setSearchFeature] = useState(null)

  const [summaryUnits, setSummaryUnits] = useState({}) // useState([{"id":"Arkansas","dams":6269,"off_network_dams":422,"miles":10.72599983215332,"barriers":3018,"off_network_barriers":1526,"layerId":"State"}]) // FIXME

  // TODO: wrap into useReducer?
  const [step, setStep] = useState('select')
  const [layer, setLayer] = useState(null) // useState('State') // FIXME

  // TODO: wrap into custom hook
  const [isLoading, setIsLoading] = useState(false)
  const [isError, setIsError] = useState(false)

  const handleSearch = useCallback(
    nextSearchFeature => {
      setSearchFeature(nextSearchFeature)
    },
    [layer]
  )

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

  const handleSelectBarrier = feature => {
    console.log(JSON.stringify(feature))
    setSelectedBarrier(feature)
  }

  const handleDetailsClose = () => {
    setSelectedBarrier(null)
  }

  let sidebarContent = null

  if (selectedBarrier === null) {
    if (isError) {
      // TODO
      sidebarContent = (
        <div className="container notification-container flex-container-column flex-justify-center flex-grow">
          <div className="notification is-error">
            <i className="fas fa-exclamation-triangle" />
            &nbsp; Whoops! There was an error loading these data. Please refresh
            your browser page and try again.
          </div>
          <p className="has-text-grey">
            If it happens again, please{' '}
            <a href="mailto:kat@southeastaquatics.net">contact us</a>.
          </p>
        </div>
      )
    } else if (isLoading) {
      // TODO
      sidebarContent = (
        <div className="loading-spinner flex-container flex-justify-center flex-align-center">
          <div className="fas fa-sync fa-spin" />
          <p>Loading...</p>
        </div>
      )
    } else {
      switch (step) {
        case 'select': {
          if (layer === null) {
            sidebarContent = <LayerChooser setLayer={handleSetLayer} />
          } else {
            sidebarContent = (
              <UnitChooser
                barrierType={barrierType}
                layer={layer}
                summaryUnits={summaryUnits}
                onBack={() => handleSetLayer(null)}
                selectUnit={handleSelectUnit}
                setSearchFeature={handleSearch}
              />
            )
          }
          break
        }
        default: {
          sidebarContent = null
        }
        // case "filter": {
        //     sidebarContent = <FiltersList />
        //     break
        // }
        // case "results": {
        //     sidebarContent = <Results />
        //     break
        // }
      }
    }
  }

  return (
    <Wrapper>
      <Sidebar>
        {selectedBarrier !== null ? (
          <BarrierDetails
            barrier={selectedBarrier}
            barrierType={barrierType}
            onClose={handleDetailsClose}
          />
        ) : (
          sidebarContent
        )}
      </Sidebar>

      <MapContainer>
        <Map
          barrierType={barrierType}
          activeLayer={layer}
          searchFeature={searchFeature}
          selectedBarrier={selectedBarrier}
          summaryUnits={summaryUnits}
          onSelectUnit={handleSelectUnit}
          onSelectBarrier={handleSelectBarrier}
        />
      </MapContainer>
    </Wrapper>
  )
}

Prioritize.propTypes = {
  barrierType: PropTypes.string.isRequired,
}

export default Prioritize
