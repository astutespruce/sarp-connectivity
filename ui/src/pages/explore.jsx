import React, { useState, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'

import { Layout, ClientOnly, SEO } from 'components/Layout'

import { ToggleButton } from 'components/Button'
import { Sidebar } from 'components/Sidebar'
import { TopBar } from 'components/Map'
import { Map, RegionSummary, UnitSummary } from 'components/Explore'
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

const ExplorePage = ({ location }) => {
  const {
    region = 'total',
    state: stateFromURL = null,
    bbox: bboxFromURL = null,
  } = getQueryParams(location)

  const [system, setSystem] = useState(stateFromURL !== null ? 'ADM' : 'HUC')
  const [focalBarrierType, setFocalBarrierType] = useState('dams') // options: dams, small_barriers, combined_barriers
  const focalBarrierTypeRef = useRef('dams') // ref that parallels above state for use in callbacks
  const [searchFeature, setSearchFeature] = useState(null)
  const [summaryUnits, setSummaryUnits] = useState([])
  const [selectedBarrier, setSelectedBarrier] = useState(null)

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
    setSummaryUnits([])
  }

  // Toggle selected unit in or out of selection
  const handleSelectUnit = (unit) => {
    const { id } = unit

    setSelectedBarrier(null)

    setSummaryUnits((prevSummaryUnits) => {
      // NOTE: we are always creating a new object,
      // because we cannot mutate the underlying object
      // without causing the setSummaryUnits call to be a no-op
      const index = prevSummaryUnits.findIndex(
        ({ id: unitId }) => unitId === id
      )

      let nextSummaryUnits = prevSummaryUnits
      if (index === -1) {
        // add it
        nextSummaryUnits = prevSummaryUnits.concat([toCamelCaseFields(unit)])
      } else {
        // remove it
        nextSummaryUnits = prevSummaryUnits
          .slice(0, index)
          .concat(prevSummaryUnits.slice(index + 1))
      }

      return nextSummaryUnits
    })
  }

  const handleReset = () => {
    setSummaryUnits([])
    setSearchFeature(null)
  }

  const handleSelectBarrier = (feature) => {
    setSelectedBarrier(feature)
    setSummaryUnits([])
  }

  const handleBarrierDetailsClose = () => {
    setSelectedBarrier(null)
  }

  const handleCreateMap = () => {
    if (stateFromURL && !searchFeature) {
      setSearchFeature({ id: stateFromURL, layer: 'State', bbox: bboxFromURL })
    }
  }

  let sidebarContent = null

  if (selectedBarrier !== null) {
    sidebarContent = (
      <BarrierDetails
        barrier={selectedBarrier}
        onClose={handleBarrierDetailsClose}
      />
    )
  } else if (summaryUnits.length > 0) {
    sidebarContent = (
      <UnitSummary
        barrierType={focalBarrierType}
        system={system}
        summaryUnits={summaryUnits}
        onSelectUnit={handleSelectUnit}
        onReset={handleReset}
      />
    )
  } else {
    sidebarContent = (
      <RegionSummary
        region={region}
        barrierType={focalBarrierType}
        system={system}
        onSearch={handleSearch}
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
              summaryUnits={summaryUnits}
              selectedBarrier={selectedBarrier}
              onSelectUnit={handleSelectUnit}
              onSelectBarrier={handleSelectBarrier}
              onCreateMap={handleCreateMap}
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
                {summaryUnits.length === 0 ? (
                  <Text
                    sx={{
                      fontSize: 'smaller',
                      color: 'grey.7',
                      lineHeight: 1.1,
                      maxWidth: '10rem',
                      ml: '0.75rem',
                    }}
                  >
                    Click on a summary unit for more information
                  </Text>
                ) : null}
              </TopBar>
            </Map>
          </Box>
        </Flex>
      </ClientOnly>
    </Layout>
  )
}

ExplorePage.propTypes = {
  location: PropTypes.object,
}

ExplorePage.defaultProps = {
  location: null,
}

export default ExplorePage

export const Head = () => <SEO title="Explore & download barriers" />
