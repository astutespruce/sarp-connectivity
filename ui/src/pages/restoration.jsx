import React, { useState, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { Layout, ClientOnly, SEO } from 'components/Layout'

import { ToggleButton } from 'components/Button'
import { Sidebar } from 'components/Sidebar'
import { TopBar } from 'components/Map'
import { Map, UnitDetails, RegionSummary } from 'components/Restoration'
import BarrierDetails from 'components/BarrierDetails'
import { SYSTEMS } from 'config'
import { toCamelCaseFields } from 'util/data'
import { getQueryParams } from 'util/dom'

const focalBarrierTypeOptions = [
  { value: 'dams', label: 'dams' },
  { value: 'small_barriers', label: 'road-related barriers' },
  { value: 'combined_barriers', label: 'both' },
]

const systemOptions = Object.entries(SYSTEMS).map(([value, label]) => ({
  value,
  label,
}))

const ProgressPage = ({ location }) => {
  const [system, setSystem] = useState('HUC')
  const [focalBarrierType, setFocalBarrierType] = useState('dams') // options: dams, small_barriers, combined_barriers
  const focalBarrierTypeRef = useRef('dams') // ref that parallels above state for use in callbacks
  const [searchFeature, setSearchFeature] = useState(null)
  const [selectedUnit, setSelectedUnit] = useState(null)
  const [selectedBarrier, setSelectedBarrier] = useState(null)
  const [metric, setMetric] = useState('gainmiles')

  const { region = 'total' } = getQueryParams(location)

  const handleSearch = useCallback((nextSearchFeature) => {
    setSearchFeature(nextSearchFeature)
  }, [])

  const handleSetFocalBarrierType = (nextType) => {
    setFocalBarrierType(nextType)
    focalBarrierTypeRef.current = nextType
    setSelectedBarrier(null)
  }

  const handleSetSystem = (nextSystem) => {
    setSystem(nextSystem)
    setSelectedUnit(null)
  }

  const handleSelectUnit = (feature) => {
    setSelectedUnit(toCamelCaseFields(feature))
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
        barrierType={focalBarrierType}
        onClose={handleDetailsClose}
      />
    )
  } else {
    sidebarContent = (
      <RegionSummary
        region={region}
        barrierType={focalBarrierType}
        system={system}
        metric={metric}
        onSearch={handleSearch}
        onChangeMetric={setMetric}
      />
    )
  }

  return (
    <Layout>
      <ClientOnly>
        <Flex sx={{ height: '100%' }}>
          <Sidebar>{sidebarContent}</Sidebar>

          <Box
            sx={{
              position: 'relative',
              height: '100%',
              flex: '1 0 auto',
            }}
          >
            <Map
              region={region}
              focalBarrierType={focalBarrierType}
              system={system}
              searchFeature={searchFeature}
              selectedUnit={selectedUnit}
              selectedBarrier={selectedBarrier}
              onSelectUnit={handleSelectUnit}
              onSelectBarrier={handleSelectBarrier}
            >
              <TopBar>
                <Text sx={{ mr: '0.5rem' }}>Show networks for:</Text>
                <ToggleButton
                  value={focalBarrierType}
                  options={focalBarrierTypeOptions}
                  onChange={handleSetFocalBarrierType}
                />
                <Text sx={{ mx: '0.5rem' }}>by</Text>
                <ToggleButton
                  value={system}
                  options={systemOptions}
                  onChange={handleSetSystem}
                />
              </TopBar>
            </Map>
          </Box>
        </Flex>
      </ClientOnly>
    </Layout>
  )
}

ProgressPage.propTypes = {
  location: PropTypes.object,
}

ProgressPage.defaultProps = {
  location: null,
}

export default ProgressPage

export const Head = () => <SEO title="Restoring aquatic connectivity" />
