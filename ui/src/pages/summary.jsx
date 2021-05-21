import React, { useState, useCallback } from 'react'

import { Flex } from 'components/Grid'
import Layout, { ClientOnly } from 'components/Layout'
import { Text } from 'components/Text'
import { ToggleButton } from 'components/Button'
import { Sidebar } from 'components/Sidebar'
import { TopBar } from 'components/Map'
import { Map, UnitDetails, SoutheastSummary } from 'components/Summary'
import BarrierDetails from 'components/BarrierDetails'
import styled from 'style'
import { SYSTEMS } from '../../config/constants'

const Wrapper = styled(Flex)`
  height: 100%;
`

const MapContainer = styled.div`
  position: relative;
  flex: 1 0 auto;
  height: 100%;
`

const barrierTypeOptions = [
  { value: 'dams', label: 'dams' },
  { value: 'barriers', label: 'road-related barriers' },
]

const systemOptions = Object.entries(SYSTEMS).map(([value, label]) => ({
  value,
  label,
}))

const SummaryPage = () => {
  const [system, setSystem] = useState('HUC')
  const [barrierType, setBarrierType] = useState('dams')
  const [searchFeature, setSearchFeature] = useState(null)
  const [selectedUnit, setSelectedUnit] = useState(null)
  const [selectedBarrier, setSelectedBarrier] = useState(null)

  const handleSearch = useCallback((nextSearchFeature) => {
    setSearchFeature(nextSearchFeature)
  }, [])

  const handleSetBarrierType = (nextBarrierType) => {
    setBarrierType(nextBarrierType)
    setSelectedBarrier(null)
  }

  const handleSetSystem = (nextSystem) => {
    setSystem(nextSystem)
    setSelectedUnit(null)
  }

  const handleSelectUnit = (feature) => {
    setSelectedUnit(feature)
    setSelectedBarrier(null)
  }

  const handleDetailsClose = () => {
    setSelectedUnit(null)
    setSearchFeature(null)
  }

  const handleSelectBarrier = (feature) => {
    setSelectedBarrier(feature)
    setSelectedUnit(null)
  }

  const handleBarrierDetailsClose = () => {
    setSelectedBarrier(null)
  }

  let sidebarContent = null

  if (selectedBarrier !== null) {
    sidebarContent = (
      <BarrierDetails
        barrier={selectedBarrier}
        onClose={handleBarrierDetailsClose}
      />
    )
  } else if (selectedUnit !== null) {
    sidebarContent = (
      <UnitDetails
        summaryUnit={selectedUnit}
        barrierType={barrierType}
        onClose={handleDetailsClose}
      />
    )
  } else {
    sidebarContent = (
      <SoutheastSummary
        barrierType={barrierType}
        system={system}
        onSearch={handleSearch}
      />
    )
  }

  return (
    <Layout title="Summarize">
      <Wrapper>
        <Sidebar>{sidebarContent}</Sidebar>

        <MapContainer>
          <ClientOnly>
            <Map
              barrierType={barrierType}
              system={system}
              searchFeature={searchFeature}
              selectedUnit={selectedUnit}
              selectedBarrier={selectedBarrier}
              onSelectUnit={handleSelectUnit}
              onSelectBarrier={handleSelectBarrier}
            />
            <TopBar>
              <Text sx={{ mr: '0.5rem' }}>Show:</Text>
              <ToggleButton
                value={barrierType}
                options={barrierTypeOptions}
                onChange={handleSetBarrierType}
              />
              <Text sx={{ mx: '0.5rem' }}>by</Text>
              <ToggleButton
                value={system}
                options={systemOptions}
                onChange={handleSetSystem}
              />
            </TopBar>
          </ClientOnly>
        </MapContainer>
      </Wrapper>
    </Layout>
  )
}

SummaryPage.propTypes = {}

export default SummaryPage
