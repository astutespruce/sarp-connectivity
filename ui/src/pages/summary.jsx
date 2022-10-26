import React, { useState, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { Layout, ClientOnly, SEO } from 'components/Layout'

import { ToggleButton } from 'components/Button'
import { Sidebar } from 'components/Sidebar'
import { TopBar } from 'components/Map'
import { Map, UnitDetails, RegionSummary } from 'components/Summary'
import BarrierDetails from 'components/BarrierDetails'
import { SYSTEMS } from 'constants'
import { toCamelCaseFields } from 'util/data'
import { getQueryParams } from 'util/dom'

const barrierTypeOptions = [
  { value: 'dams', label: 'dams' },
  { value: 'small_barriers', label: 'road-related barriers' },
]

const systemOptions = Object.entries(SYSTEMS).map(([value, label]) => ({
  value,
  label,
}))

const SummaryPage = ({ location }) => {
  const [system, setSystem] = useState('HUC')
  const [barrierType, setBarrierType] = useState('dams')
  const barrierTypeRef = useRef('dams') // ref that parallels above state for use in callbacks
  const [searchFeature, setSearchFeature] = useState(null)
  const [selectedUnit, setSelectedUnit] = useState(null)
  const [selectedBarrier, setSelectedBarrier] = useState(null)

  const { region = 'total' } = getQueryParams(location)

  const handleSearch = useCallback((nextSearchFeature) => {
    setSearchFeature(nextSearchFeature)
  }, [])

  const handleSetBarrierType = (nextBarrierType) => {
    setBarrierType(nextBarrierType)
    barrierTypeRef.current = nextBarrierType
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
    console.log('selected:', feature)

    // promote appropriate network results
    if (feature && feature.barrierType === 'waterfalls') {
      const curBarrierType = barrierTypeRef.current
      const networkFields = {}
      Object.keys(feature)
        .filter((k) => k.endsWith(curBarrierType))
        .forEach((field) => {
          networkFields[field.split('_')[0]] = feature[field]
        })
      setSelectedBarrier({
        ...feature,
        ...networkFields,
      })
    } else {
      setSelectedBarrier(feature)
    }

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
      <RegionSummary
        region={region}
        barrierType={barrierType}
        system={system}
        onSearch={handleSearch}
      />
    )
  }

  return (
    <Layout>
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
              region={region}
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

SummaryPage.propTypes = {
  location: PropTypes.object,
}

SummaryPage.defaultProps = {
  location: null,
}

export default SummaryPage

export const Head = () => <SEO title="Summarize barriers" />
