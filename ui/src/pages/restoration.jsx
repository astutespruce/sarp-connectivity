import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Spinner, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { fetchUnitDetails } from 'components/Data'
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
  const { region = 'total', state: stateFromURL = null } =
    getQueryParams(location)

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
    system: stateFromURL !== null ? 'ADM' : 'HUC',
    focalBarrierType: 'dams', // options: dams, small_barriers, combined_barriers
    summaryUnits: [],
    selectedBarrier: null,
    metric: 'gainmiles',
    isUnitError: false,
    isUnitLoading: false,
  }))

  const {
    isLoading,
    error,
    data: selectedStateFromURL = null,
  } = useQuery({
    queryKey: [stateFromURL],
    queryFn: async () => fetchUnitDetails('State', stateFromURL),
    enabled: stateFromURL !== null,
    staleTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const queryClient = useQueryClient()

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
    }))
  }

  // Toggle selected unit in or out of selection
  const handleSelectUnit = ({ layer, id, ...preFetchedUnitData }) => {
    let needsFetchUnit = false
    setState((prevState) => {
      const index = prevState.summaryUnits.findIndex(
        ({ id: unitId }) => unitId === id
      )

      if (index >= 0) {
        // remove it
        return {
          ...prevState,
          summaryUnits: prevState.summaryUnits
            .slice(0, index)
            .concat(prevState.summaryUnits.slice(index + 1)),
        }
      }

      // assume if unitData are present it was from a search feature
      if (Object.keys(preFetchedUnitData).length > 0) {
        return {
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
        }
      }

      // fetch then add it
      needsFetchUnit = true
      return {
        ...prevState,
        isUnitError: false,
        isUnitLoading: true,
      }
    })

    if (needsFetchUnit) {
      queryClient
        .fetchQuery({
          queryKey: [layer, id],
          queryFn: async () => fetchUnitDetails(layer, id),
        })
        .then((unitData) => {
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

  const handleCreateMap = () => {
    if (selectedStateFromURL !== null) {
      // NOTE: need to do this after map has loaded!
      handleSelectUnit(selectedStateFromURL)
    }
  }

  const handleSetMetric = (newMetric) => {
    setState((prevState) => ({ ...prevState, metric: newMetric }))
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
        metric={metric}
        onChangeMetric={handleSetMetric}
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
                  region={region}
                  bounds={
                    selectedStateFromURL !== null
                      ? selectedStateFromURL.bbox.split(',').map(parseFloat)
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

ProgressPage.propTypes = {
  location: PropTypes.object,
}

ProgressPage.defaultProps = {
  location: null,
}

export default ProgressPage

export const Head = () => <SEO title="Restoring aquatic connectivity" />
