import React, { useState, useCallback, useRef } from 'react'
import PropTypes from 'prop-types'
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
import {
  ExportMap,
  LocatorMap,
  mapToDataURL,
  basemapAttribution,
} from 'components/Map'

import { PageError } from 'components/Layout'

import Construction from './Construction'
import Contact from './Contact'
import Credits from './Credits'
import Feasibility from './Feasibility'
import Header from './Header'
import IDInfo from './IDInfo'
import Legend from './Legend'
import Location from './Location'
import MapAttribution from './MapAttribution'
import Network from './Network'
import Scores from './Scores'
import Species from './Species'

const Preview = ({ barrierType, data }) => {
  const { id, sarpid, name, upnetid, county, state, lat, lon, hasnetwork } =
    data
  const initCenter = [lon, lat]

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
      console.log('bounds updated')
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
        barrier={data}
      />
    )
      .toBlob()
      .then((blob) => {
        setState((prevState) => ({
          ...prevState,
          isPending: false,
          hasError: false,
        }))
        saveAs(blob, `${sarpid}_barrier_report.pdf`)
      })
      .catch((error) => {
        // TODO: log to sentry?
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
              <Button onClick={handleExport}>Export to PDF</Button>
            )}
          </Box>
        </Flex>

        <Header name={name} county={county} state={state} lat={lat} lon={lon} />

        <ExportMap
          barrierID={id}
          networkID={upnetid}
          center={initCenter}
          zoom={13.5}
          barrierType={barrierType}
          onCreateMap={handleCreateExportMap}
          onUpdateBasemap={handleUpdateBasemap}
        />

        <MapAttribution attribution={attribution} />

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

        <Flex sx={{ justifyContent: 'space-between', mt: '3rem' }}>
          <Box sx={{ flex: '1 1 auto', width: '50%', mr: '2rem' }}>
            <Location {...data} />
          </Box>
          <Box sx={{ flex: '1 1 auto', width: '50%' }}>
            <Construction {...data} />
          </Box>
        </Flex>

        <Flex sx={{ justifyContent: 'space-between', mt: '3rem' }}>
          <Box sx={{ flex: '1 1 auto', width: '50%', mr: '2rem' }}>
            <Network {...data} />
          </Box>
          {hasnetwork ? (
            <Box sx={{ flex: '1 1 auto', width: '50%' }}>
              <Scores barrierType={barrierType} {...data} />
            </Box>
          ) : null}
        </Flex>

        <Box sx={{ mt: '3rem' }}>
          <Species {...data} />
        </Box>

        <Box sx={{ mt: '3rem' }}>
          <Feasibility {...data} />
        </Box>

        <Box sx={{ mt: '3rem' }}>
          <IDInfo {...data} />
        </Box>

        <Box sx={{ mt: '3rem' }}>
          <Contact barrierType={barrierType} {...data} />
        </Box>

        <Box sx={{ mt: '2rem' }}>
          <Credits />
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
