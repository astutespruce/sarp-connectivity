import React, { useRef, useState } from 'react'
import PropTypes from 'prop-types'

import { Flex, Box } from 'components/Grid'
import Sidebar from 'components/Sidebar'
import BarrierDetails from 'components/BarrierDetails'
import { Map } from 'components/Map'
import styled from 'style'

// import UnitChooser from './UnitChooser'
import LayerChooser from './LayerChooser'

const Wrapper = styled(Flex)`
  height: 100%;
`

const SidebarContent = styled(Box).attrs({ p: '1rem' })`
overflow-y: auto;
overflow-x: hidden;
flex-grow: 1;
`

const MapContainer = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
`

const Prioritize = ({ barrierType }) => {
    const mapRef = useRef(null)
  const [selectedBarrier, setSelectedBarrier] = useState(null)
  const [searchFeature, setSearchFeature] = useState(null)

  // TODO: wrap into useReducer?
  const [step, setStep] = useState('select')
  const [system, setSystem] = useState(null)
  const [layer, setLayer] = useState(null)

  // TODO: wrap into custom hook
  const [isLoading, setIsLoading] = useState(false)
  const [isError, setIsError] = useState(false)

  const handleCreateMap = (map) => {
    mapRef.current = map

    // TODO
  }

  const handleSearch = nextSearchFeature => {
    setSearchFeature(nextSearchFeature)
  }

  const handleSetSystem = nextSystem => {
    setSystem(nextSystem)
    selectedBarrier(null)
  }

  const handleSetLayer = nextLayer => {
      setLayer(nextLayer)
  }

  const handleSelectBarrier = feature => {
    setSelectedBarrier(feature)
  }

  const handleDetailsClose = () => {
    selectedBarrier(null)
    setSearchFeature(null)
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
            sidebarContent = <LayerChooser setLayer={handleSetLayer}/>
          } 
        //   else {
        //     sidebarContent = <UnitChooser />
        //   }
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
          <BarrierDetails barrier={selectedBarrier} barrierType={barrierType}/>
        ) : (
          <SidebarContent>{sidebarContent}</SidebarContent>
        )}
      </Sidebar>

      <MapContainer>
        <Map
          barrierType={barrierType}
          system={system}
          searchFeature={searchFeature}
          selectedBarrier={selectedBarrier}
          onSelectUnit={handleSelectBarrier}
          onCreateMap={handleCreateMap}
        />
      </MapContainer>
    </Wrapper>
  )
}

Prioritize.propTypes = {
  barrierType: PropTypes.string.isRequired,
}

export default Prioritize
