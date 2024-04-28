import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Spinner, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import {
  fetchUnitDetails,
  useSummaryData,
  useRegionSummary,
} from 'components/Data'
import {
  Layout,
  ClientOnly,
  SEO,
  PageError,
  PageLoading,
} from 'components/Layout'
import { ToggleButton } from 'components/Button'
import { Sidebar } from 'components/Sidebar'
import { TopBar } from 'components/Map'
import { Map, RegionSummary, UnitSummary } from 'components/Explore'
import BarrierDetails from 'components/BarrierDetails'
import { REGIONS, SYSTEMS } from 'config'
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
  const queryClient = useQueryClient()
  const summary = useSummaryData()
  const regions = useRegionSummary()

  const {
    region = 'total',
    state: stateFromURL = null,
    fishhabitatpartnership: fishhabitatpartnershipFromURL = null,
  } = getQueryParams(location)

  const idFromURL = stateFromURL || fishhabitatpartnershipFromURL
  let idFromURLType = null
  if (stateFromURL) {
    idFromURLType = 'State'
  } else if (fishhabitatpartnershipFromURL) {
    idFromURLType = 'FishHabitatPartnership'
  }

  const [
    {
      system,
      focalBarrierType,
      summaryUnits,
      selectedBarrier,
      isUnitError,
      isUnitLoading,
    },
    setState,
  ] = useState(() => ({
    system: idFromURL !== null ? 'ADM' : 'HUC',
    focalBarrierType: 'dams', // options: dams, small_barriers, combined_barriers
    summaryUnits: [],
    selectedBarrier: null,
    isUnitError: false,
    isUnitLoading: false,
  }))

  const summaryUnitsRef = useRef(new Set())

  // load data for selected state specified in URL
  const {
    isLoading,
    error,
    data: selectedItemFromURL = null,
  } = useQuery({
    queryKey: [idFromURL],
    queryFn: async () => fetchUnitDetails(idFromURLType, idFromURL),
    enabled: idFromURL !== null,
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  console.log('selected item', selectedItemFromURL)

  const handleSetFocalBarrierType = (nextType) => {
    setState((prevState) => ({
      ...prevState,
      focalBarrierType: nextType,
      selectedBarrier: null,
    }))
  }

  const handleSetSystem = (nextSystem) => {
    setState((prevState) => ({
      ...prevState,
      system: nextSystem,
      summaryUnits: [],
      isUnitError: false,
      isUnitLoading: false,
    }))
  }

  // Toggle selected unit in or out of selection
  const handleSelectUnit = ({ layer, id, ...preFetchedUnitData }) => {
    if (summaryUnitsRef.current.has(id)) {
      // remove it
      summaryUnitsRef.current.delete(id)
      setState((prevState) => ({
        ...prevState,
        isUnitError: false,
        isUnitLoading: false,
        summaryUnits: prevState.summaryUnits.filter(
          ({ id: unitId }) => unitId !== id
        ),
      }))
      return
    }

    // add it
    // assume if unitData are present it was from a search feature and already
    // has necessary data loaded
    if (Object.keys(preFetchedUnitData).length > 0) {
      summaryUnitsRef.current.add(id)
      setState((prevState) => ({
        ...prevState,
        isUnitError: false,
        isUnitLoading: false,
        summaryUnits: prevState.summaryUnits.concat([
          toCamelCaseFields({
            layer,
            id,
            ...preFetchedUnitData,
          }),
        ]),
      }))
      return
    }

    queryClient
      .fetchQuery({
        queryKey: [layer, id],
        queryFn: async () => fetchUnitDetails(layer, id),
      })
      .then((unitData) => {
        if (summaryUnitsRef.current.has(id)) {
          // if multiple requests resolved with this id due to slow requests
          setState((prevState) => ({
            ...prevState,
            isUnitError: false,
            isUnitLoading: false,
          }))
          return
        }

        summaryUnitsRef.current.add(id)
        setState((prevState) => ({
          ...prevState,
          isUnitError: false,
          isUnitLoading: false,
          summaryUnits: prevState.summaryUnits.concat([
            toCamelCaseFields(unitData),
          ]),
        }))
      })
      .catch(() => {
        setState((prevState) => ({
          ...prevState,
          isUnitError: true,
          isUnitLoading: false,
        }))
      })
  }

  const handleReset = () => {
    setState((prevState) => ({
      ...prevState,
      summaryUnits: [],
      searchFeature: null,
      selectedBarrier: null,
      isUnitError: false,
      isUnitLoading: false,
    }))
  }

  const handleSelectBarrier = (feature) => {
    setState((prevState) => ({
      ...prevState,
      selectedBarrier: feature,
      summaryUnits: [],
    }))
  }

  const handleBarrierDetailsClose = () => {
    setState((prevState) => ({
      ...prevState,
      selectedBarrier: null,
    }))
  }

  const handleCreateMap = () => {
    if (stateFromURL !== null && selectedItemFromURL) {
      // NOTE: need to do this after map has loaded!
      handleSelectUnit(selectedItemFromURL)
    }
  }

  let regionData = {}
  if (fishhabitatpartnershipFromURL && selectedItemFromURL) {
    regionData = toCamelCaseFields(selectedItemFromURL)
  } else if (region !== 'total') {
    regionData = {
      ...regions[region],
      name: `${REGIONS[region].name} Region`,
      layer: 'regions',
    }
  } else {
    regionData = summary
  }

  let sidebarContent = null

  if (isUnitError) {
    sidebarContent = (
      <Flex
        sx={{
          alignItems: 'center',
          flexDirection: 'column',
          p: '1rem',
          mt: '2rem',
          flex: '1 1 auto',
        }}
      >
        <Flex sx={{ color: 'highlight', alignItems: 'center' }}>
          <ExclamationTriangle size="2em" />
          <Text sx={{ ml: '0.5rem', fontSize: '2rem' }}>Whoops!</Text>
        </Flex>
        There was an error loading these data. Please try clicking on a
        different barrier or refresh this page in your browser.
        <Text variant="help" sx={{ mt: '2rem' }}>
          If it happens again, please{' '}
          <a href="mailto:kat@southeastaquatics.net">contact us</a>.
        </Text>
      </Flex>
    )
  } else if (isUnitLoading) {
    sidebarContent = (
      <Flex
        sx={{
          alignItems: 'center',
          flexDirection: 'column',
          p: '1rem',
          mt: '2rem',
          flex: '1 1 auto',
        }}
      >
        <Flex sx={{ alignItems: 'center', gap: '0.5rem' }}>
          <Spinner size="2rem" />
          <Text>Loading details...</Text>
        </Flex>
      </Flex>
    )
  } else if (selectedBarrier !== null) {
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
        barrierType={focalBarrierType}
        region={region}
        {...regionData}
        system={system}
        onSelectUnit={handleSelectUnit}
      />
    )
  }

  return (
    <Layout>
      <ClientOnly>
        <Flex sx={{ height: '100%' }}>
          {error ? <PageError /> : null}

          {isLoading && !error ? <PageLoading /> : null}

          {!(error || isLoading) ? (
            <>
              <Sidebar>{sidebarContent}</Sidebar>

              <Box
                sx={{
                  position: 'relative',
                  height: '100%',
                  flex: '1 0 auto',
                }}
              >
                <Map
                  // FIXME: cleanup passing of region
                  region={fishhabitatpartnershipFromURL || region}
                  bounds={
                    selectedItemFromURL !== null
                      ? selectedItemFromURL.bbox.split(',').map(parseFloat)
                      : null
                  }
                  focalBarrierType={focalBarrierType}
                  system={system}
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
            </>
          ) : null}
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
