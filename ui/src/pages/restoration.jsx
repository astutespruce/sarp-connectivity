import React, { useMemo, useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Spinner, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { fetchUnitDetails, useSummaryData } from 'components/Data'
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
import { Map, UnitSummary, RegionSummary } from 'components/Restoration'
import BarrierDetails from 'components/BarrierDetails'
import { REGIONS, SYSTEMS, FISH_HABITAT_PARTNERSHIPS } from 'config'
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
  const queryClient = useQueryClient()
  const summary = useSummaryData()

  const {
    region = null,
    state = null,
    fishhabitatpartnership = null,
  } = getQueryParams(location)

  const urlItemId = state || fishhabitatpartnership || region
  let urlItemType = null
  if (region) {
    urlItemType = 'Region'
  } else if (state) {
    urlItemType = 'State'
  } else if (fishhabitatpartnership) {
    urlItemType = 'FishHabitatPartnership'
  }

  const [
    {
      system,
      focalBarrierType,
      summaryUnits,
      selectedBarrier,
      metric,
      isUnitError,
      isUnitLoading,
    },
    setState,
  ] = useState(() => ({
    system: urlItemId !== null ? 'ADM' : 'HUC',
    focalBarrierType: 'dams', // options: dams, small_barriers, combined_barriers
    summaryUnits: [],
    selectedBarrier: null,
    metric: 'gainmiles',
    isUnitError: false,
    isUnitLoading: false,
  }))

  const summaryUnitsRef = useRef(new Set())

  // load data for item specified in URL
  const {
    isLoading,
    error,
    data: selectedItem = null,
  } = useQuery({
    queryKey: [urlItemType, urlItemId],
    queryFn: async () => fetchUnitDetails(urlItemType, urlItemId),
    enabled: urlItemId !== null,
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

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
  const handleSelectUnit = ({
    layer,
    id: selectedId,
    ...preFetchedUnitData
  }) => {
    if (summaryUnitsRef.current.has(selectedId)) {
      // remove it
      summaryUnitsRef.current.delete(selectedId)
      setState((prevState) => ({
        ...prevState,
        isUnitError: false,
        isUnitLoading: false,
        summaryUnits: prevState.summaryUnits.filter(
          ({ id: unitId }) => unitId !== selectedId
        ),
      }))
      return
    }

    // add it
    // assume if unitData are present it was from a search feature and already
    // has necessary data loaded
    if (Object.keys(preFetchedUnitData).length > 0) {
      summaryUnitsRef.current.add(selectedId)
      setState((prevState) => ({
        ...prevState,
        isUnitError: false,
        isUnitLoading: false,
        summaryUnits: prevState.summaryUnits.concat([
          {
            layer,
            id: selectedId,
            ...preFetchedUnitData,
          },
        ]),
      }))
      return
    }

    queryClient
      .fetchQuery({
        queryKey: [layer, selectedId],
        queryFn: async () => fetchUnitDetails(layer, selectedId),
      })
      .then((unitData) => {
        if (summaryUnitsRef.current.has(selectedId)) {
          // if multiple requests resolved with this id due to slow requests
          setState((prevState) => ({
            ...prevState,
            isUnitError: false,
            isUnitLoading: false,
          }))
          return
        }

        summaryUnitsRef.current.add(selectedId)
        setState((prevState) => ({
          ...prevState,
          isUnitError: false,
          isUnitLoading: false,
          summaryUnits: prevState.summaryUnits.concat([unitData]),
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

  const handleSetMetric = (newMetric) => {
    setState((prevState) => ({ ...prevState, metric: newMetric }))
  }

  const regionData = useMemo(
    () => {
      if (selectedItem) {
        const bounds = selectedItem.bbox.split(',').map((d) => parseFloat(d))
        if (region) {
          return {
            ...selectedItem,
            layer: 'boundary',
            bounds,
            name: `the ${REGIONS[region].name}`,
            url: REGIONS[region].url,
            urlLabel: 'view region page for more information',
          }
        }
        if (fishhabitatpartnership) {
          return {
            ...selectedItem,
            layer: 'fhp_boundary',
            bounds,
            name: `the ${FISH_HABITAT_PARTNERSHIPS[fishhabitatpartnership].name}`,
            url: `/fhp/${fishhabitatpartnership}`,
            urlLabel:
              'view the Fish Habitat Partnership page for more information',
          }
        }
        if (state) {
          return {
            ...selectedItem,
            layer: 'State',
            bounds,
            url: `/states/${state}`,
            urlLabel: `view state page for more information`,
          }
        }
      }

      return {
        ...summary,
        id: 'total',
        name: 'full analysis region',
        layer: 'boundary',
      }
    },
    // ignore other deps intentionally
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [selectedItem]
  )

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
        metric={metric}
        onChangeMetric={handleSetMetric}
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
        metric={metric}
        onSelectUnit={handleSelectUnit}
        onChangeMetric={handleSetMetric}
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
                  region={regionData}
                  focalBarrierType={focalBarrierType}
                  system={system}
                  summaryUnits={summaryUnits}
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

ProgressPage.propTypes = {
  location: PropTypes.object,
}

ProgressPage.defaultProps = {
  location: null,
}

export default ProgressPage

export const Head = () => <SEO title="Restoring aquatic connectivity" />
