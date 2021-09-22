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

import { Report } from 'components/Report'
import { mapToDataURL, basemapAttribution } from 'components/Map'

import { PageError } from 'components/Layout'

import LocationConstruction from './LocationConstruction'
import Contact from './Contact'
import Credits from './Credits'
import Feasibility from './Feasibility'
import Header from './Header'
import IDInfo from './IDInfo'
import Legend from './Legend'
import { Attribution, LocatorMap, Map } from './Map'
import Network from './Network'
import Scores from './Scores'
import Species from './Species'

const Preview = ({ barrierType, data }) => {
  const { id, sarpid, upnetid, county, state, lat, lon } = data

  const name =
    data.name || barrierType === 'dams'
      ? `Dam: unknown name (SARPID: ${sarpid})`
      : `Road-related barrier: unknown name (SARPID ${sarpid})`

  const [{ attribution, hasError, isPending }, setState] = useState({
    attribution: basemapAttribution['light-v9'],
    hasError: false,
    isPending: false,
  })

  const exportMapRef = useRef(null)
  const locatorMapRef = useRef(null)

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

  const handleExport = useCallback(async () => {
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
        data={data}
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
  }, [])

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
          name={name}
          county={county}
          state={state}
          lat={lat}
          lon={lon}
        />

        <Map
          barrierID={id}
          networkID={upnetid}
          center={[lon, lat]}
          zoom={13.5}
          barrierType={barrierType}
          onCreateMap={handleCreateExportMap}
          onUpdateBasemap={handleUpdateBasemap}
        />

        <Attribution attribution={attribution} />

        <Flex sx={{ mt: '2rem' }}>
          <Box sx={{ flex: '0 0 auto', mr: '2rem' }}>
            <LocatorMap
              center={[lon, lat]}
              zoom={5}
              onCreateMap={handleCreateLocatorMap}
            />
          </Box>
          <Legend barrierType={barrierType} name={name} />
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

          <Network sx={{ mt: '3rem' }} barrierType={barrierType} {...data} />

          <Scores sx={{ mt: '3rem' }} barrierType={barrierType} {...data} />

          <Feasibility sx={{ mt: '3rem' }} {...data} />

          <Species sx={{ mt: '3rem' }} {...data} />

          <IDInfo sx={{ mt: '3rem' }} {...data} />

          <Contact sx={{ mt: '3rem' }} barrierType={barrierType} {...data} />

          <Credits sx={{ mt: '2rem' }} />
        </Box>
      </Container>
    </Box>
  )
}

Preview.propTypes = {
  barrierType: PropTypes.string.isRequired,
  data: PropTypes.shape({
    id: PropTypes.number.isRequired,
    sarpid: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    lat: PropTypes.number.isRequired,
    lon: PropTypes.number.isRequired,
    county: PropTypes.string.isRequired,
    state: PropTypes.string.isRequired,
    upnetid: PropTypes.number,
    hasnetwork: PropTypes.bool,
    // other props validated by subcomponents
  }).isRequired,
}

export default Preview
