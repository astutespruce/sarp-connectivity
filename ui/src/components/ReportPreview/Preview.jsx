// @refresh reset

import React, { useState, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
import { FilePdf } from '@emotion-icons/fa-solid'
import {
  Box,
  Container,
  Flex,
  Button,
  Spinner,
  Paragraph,
  Text,
} from 'theme-ui'
import { pdf } from '@react-pdf/renderer'
import { saveAs } from 'file-saver'

import { barrierNameWhenUnknown } from 'config'
import { extractHabitat } from 'components/Data/Habitat'
import { Report } from 'components/Report'
import { mapToDataURL, basemapAttribution } from 'components/Map'
import { isEmptyString } from 'util/string'

import { PageError } from 'components/Layout'

import LocationConstruction from './LocationConstruction'
import Contact from './Contact'
import Credits from './Credits'
import DiadromousInfo from './DiadromousInfo'
import Feasibility from './Feasibility'
import Header from './Header'
import IDInfo from './IDInfo'
import Legend from './Legend'
import { Attribution, LocatorMap, Map } from './Map'
import Network from './Network'
import Scores from './Scores'
import SpeciesHabitat from './SpeciesHabitat'
import SpeciesWatershedPresence from './SpeciesWatershedPresence'

const Preview = ({ networkType, data }) => {
  const {
    id,
    sarpid,
    upnetid,
    county,
    state,
    lat,
    lon,
    feasibilityclass,
    removed,
    hasnetwork,
    flowstoocean,
    milestooutlet,
  } = data

  const barrierType =
    networkType === 'combined_barriers' ||
    networkType === 'largefish_barriers' ||
    networkType === 'smallfish_barriers'
      ? data.barriertype
      : networkType

  const name = !isEmptyString(data.name)
    ? data.name
    : barrierNameWhenUnknown[barrierType] || 'Unknown name'

  const habitat = hasnetwork ? extractHabitat(data) : []

  const [{ attribution, hasError, isPending, visibleLayers }, setState] =
    useState({
      attribution: basemapAttribution['light-v10'],
      hasError: false,
      isPending: false,
      visibleLayers: null,
    })

  const exportMapRef = useRef(null)
  const locatorMapRef = useRef(null)

  const handleVisibleLayerUpdate = useCallback((visible) => {
    setState((prevState) => ({ ...prevState, visibleLayers: visible }))
  }, [])

  const handleCreateExportMap = useCallback((map) => {
    exportMapRef.current = map

    map.on('moveend', () => {
      const [ll, ur] = map.getBounds().toArray()
      setState((prevState) => ({
        ...prevState,
        center: map.getCenter().toArray(),
        bounds: [...ll, ...ur],
      }))
    })
  }, [])

  const handleCreateLocatorMap = useCallback((map) => {
    locatorMapRef.current = map
  }, [])

  const handleUpdateBasemap = useCallback((basemapID) => {
    setState((prevState) => ({
      ...prevState,
      attribution: basemapAttribution[basemapID],
    }))
  }, [])

  const handleExport = useCallback(
    async () => {
      if (!(locatorMapRef.current && exportMapRef.current)) {
        // not done loading yet
        return
      }

      setState((prevState) => ({
        ...prevState,
        isPending: true,
        hasError: false,
      }))

      const [mapImage, locatorMapImage] = await Promise.all([
        mapToDataURL(exportMapRef.current),
        mapToDataURL(locatorMapRef.current),
      ])

      // get scale component
      let scale = null
      const scaleNode = window.document.querySelector('.mapboxgl-ctrl-scale')
      if (scaleNode) {
        scale = {
          width: scaleNode.offsetWidth,
          label: scaleNode.innerText,
        }
      }

      pdf(
        <Report
          map={mapImage}
          scale={scale}
          attribution={attribution}
          locatorMap={locatorMapImage}
          barrierType={barrierType}
          networkType={networkType}
          data={data}
          name={name}
          visibleLayers={visibleLayers}
        />
      )
        .toBlob()
        .then((blob) => {
          setState((prevState) => ({
            ...prevState,
            isPending: false,
            hasError: false,
          }))
          saveAs(
            blob,
            `${sarpid}_${
              barrierType === 'dams' ? 'dam' : 'road_related_barrier'
            }_report.pdf`
          )
        })
        .catch((error) => {
          console.error(error)
          setState((prevState) => ({
            ...prevState,
            isPending: false,
            hasError: true,
          }))
        })
    },
    // intentionally omitting other deps; they don't change
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
    [visibleLayers]
  )

  if (hasError) {
    return <PageError />
  }

  return (
    <Box sx={{ overflow: 'auto', height: '100%', fontFamily: 'Helvetica' }}>
      <Container sx={{ width: '540pt', pb: '4rem', mb: '4rem' }}>
        <Flex
          sx={{
            justifyContent: 'space-between',
            mb: '1rem',
            borderBottom: '1px solid',
            borderBottomColor: 'grey.1',
            pb: '1rem',
          }}
        >
          <Paragraph variant="help" sx={{ flex: '1 1 auto', mr: '2rem' }}>
            Use the map below to define the extent and basemap you want visible
            in your PDF.
          </Paragraph>
          <Box sx={{ flex: '0 0 auto' }}>
            {isPending ? (
              <Button disabled variant="disabled">
                <Flex sx={{ alignItems: 'center' }}>
                  <Box sx={{ flex: '0 0 auto', mr: '0.5rem' }}>
                    <Spinner size="1em" />
                  </Box>
                  <Text sx={{ flex: '0 0 auto' }}>creating PDF...</Text>
                </Flex>
              </Button>
            ) : (
              <Button onClick={handleExport}>
                <Flex sx={{ alignItems: 'center' }}>
                  <Box sx={{ flex: '0 0 auto', mr: '0.5rem' }}>
                    <FilePdf size="1em" />
                  </Box>
                  <Text sx={{ flex: '0 0 auto' }}>Export to PDF</Text>
                </Flex>
              </Button>
            )}
          </Box>
        </Flex>

        <Header
          barrierType={barrierType}
          {...data}
          name={name}
          county={county}
          state={state}
          lat={lat}
          lon={lon}
        />

        <Map
          barrierID={id}
          networkID={removed ? id : upnetid}
          center={[lon, lat]}
          zoom={13.5}
          networkType={networkType}
          removed={removed}
          onCreateMap={handleCreateExportMap}
          onUpdateBasemap={handleUpdateBasemap}
          onVisibleLayerUpdate={handleVisibleLayerUpdate}
        />

        <Attribution attribution={attribution} />

        <Flex sx={{ mt: '1rem' }}>
          <Box sx={{ flex: '0 0 auto', mr: '2rem' }}>
            <LocatorMap
              center={[lon, lat]}
              zoom={5}
              onCreateMap={handleCreateLocatorMap}
            />
          </Box>
          <Legend
            networkType={networkType}
            name={name}
            visibleLayers={visibleLayers}
          />
        </Flex>

        <Box
          sx={{
            h3: {
              bg: 'grey.1',
              py: '0.5rem',
              px: '1rem',
              mb: '0.5rem',
            },
          }}
        >
          <LocationConstruction
            sx={{ mt: '3rem' }}
            barrierType={barrierType}
            {...data}
          />

          <Network
            sx={{ mt: '3rem' }}
            barrierType={barrierType}
            networkType={networkType}
            {...data}
          />

          <Scores
            sx={{ mt: '3rem' }}
            barrierType={barrierType}
            networkType={networkType}
            {...data}
          />

          {!removed &&
          feasibilityclass !== null &&
          feasibilityclass > 0 &&
          feasibilityclass <= 10 ? (
            <Feasibility sx={{ mt: '3rem' }} {...data} />
          ) : null}

          {hasnetwork && habitat.length > 0 ? (
            <SpeciesHabitat sx={{ mt: '3rem' }} habitat={habitat} />
          ) : null}

          {hasnetwork && flowstoocean && milestooutlet < 500 ? (
            <DiadromousInfo
              sx={{ mt: '3rem' }}
              barrierType={barrierType}
              {...data}
            />
          ) : null}

          <SpeciesWatershedPresence
            sx={{ mt: '3rem' }}
            barrierType={barrierType}
            {...data}
          />

          <IDInfo sx={{ mt: '3rem' }} {...data} />

          <Contact sx={{ mt: '3rem' }} barrierType={barrierType} {...data} />

          <Credits sx={{ mt: '2rem' }} />
        </Box>
      </Container>
    </Box>
  )
}

Preview.propTypes = {
  networkType: PropTypes.string.isRequired,
  data: PropTypes.shape({
    id: PropTypes.number.isRequired,
    barriertype: PropTypes.string,
    sarpid: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    lat: PropTypes.number.isRequired,
    lon: PropTypes.number.isRequired,
    county: PropTypes.string.isRequired,
    state: PropTypes.string.isRequired,
    feasibilityclass: PropTypes.number,
    upnetid: PropTypes.number,
    removed: PropTypes.bool,
    hasnetwork: PropTypes.bool,
    flowstoocean: PropTypes.number,
    milestooutlet: PropTypes.number,
    // other props validated by subcomponents
  }).isRequired,
}

export default Preview
