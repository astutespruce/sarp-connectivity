import React, { useState, useCallback } from 'react'
import { Box, Flex, Text } from 'theme-ui'

import Layout, { ClientOnly } from 'components/Layout'

import { ToggleButton } from 'components/Button'
import { Sidebar } from 'components/Sidebar'
import { TopBar } from 'components/Map'
import { Map, UnitDetails, SoutheastSummary } from 'components/Summary'
import BarrierDetails from 'components/BarrierDetails'

import { SYSTEMS } from '../../config/constants'

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
    console.log(JSON.stringify(feature))
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
      <Flex sx={{ height: '100%' }}>
        <Sidebar>{sidebarContent}</Sidebar>

        <Box
          sx={{
            position: 'relative',
            height: '100%',
            flex: '1 0 auto',
          }}
        >
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
        </Box>
      </Flex>
    </Layout>
  )
}

SummaryPage.propTypes = {}

export default SummaryPage
