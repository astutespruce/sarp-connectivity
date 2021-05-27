import React, { useState, useCallback, useRef } from 'react'
import {
  Box,
  Container,
  Flex,
  Button,
  Image,
  Spinner,
  Paragraph,
  Text,
} from 'theme-ui'
import { pdf } from '@react-pdf/renderer'
import { saveAs } from 'file-saver'

import { BarrierReport } from 'components/Report'
import {
  Construction,
  Contact,
  Credits,
  Feasibility,
  Header,
  IDInfo,
  Legend,
  Location,
  MapAttribution,
  Network,
  Scores,
  Species,
} from 'components/ReportPreview'
import {
  ExportMap,
  LocatorMap,
  mapToDataURL,
  basemapAttribution,
} from 'components/Map'

import { PageError } from 'components/Layout'

const initBounds = [
  -81.75491755391782, 34.202167532091835, -81.71679157217531,
  34.225793798992214,
]
const barrierType = 'dams'
const initZoom = 13.5
const initCenter = [-81.73324540257454, 34.214985614638195]

const barrier = {
  id: 109572,
  name: 'John Wilson Dam',
  sarpid: 'SC2527',
  nidid: 'SC02841',
  source: 'SEACAP-Unsnapped:  Unique NID 2013 dams not found*',
  river: 'Turner Branch',
  year: 0,
  height: 22,
  construction: 6,
  purpose: 1,
  condition: 0,
  passagefacility: 0,
  recon: 0,
  feasibility: 0,
  tespp: 0,
  statesgcnspp: 6,
  regionalsgcnspp: 0,
  ownertype: 1,
  protectedland: 0,
  huc8_usfs: 0,
  huc8_coa: 0,
  huc8_sgcn: 1,
  basin: 'Santee',
  HUC6: '030501',
  HUC8: '03050109',
  HUC12: '030501090908',
  State: 'South Carolina',
  countyname: 'Newberry',
  ECO3: '8.3.4',
  ECO4: '45b',
  streamorder: 2,
  landcover: 85,
  sinuosity: 1.034000039100647,
  sizeclasses: 0,
  totalupstreammiles: 1.8530000448226929,
  totaldownstreammiles: 2741.5029296875,
  freeupstreammiles: 1.3450000286102295,
  freedownstreammiles: 2381.72607421875,
  se_nc_tier: 18,
  se_wc_tier: 13,
  se_ncwc_tier: 15,
  state_nc_tier: 10,
  state_wc_tier: 12,
  state_ncwc_tier: 11,
  heightclass: 3,
  passagefacilityclass: 0,
  gainmilesclass: 1,
  tesppclass: 0,
  statesgcnsppclass: 3,
  regionalsgcnsppclass: 0,
  streamorderclass: 2,
  County: '45071',
  sinuosityclass: 0,
  upnetid: 3014872,
  downnetid: 3779393756,
  HUC8Name: 'Saluda',
  HUC12Name: 'Lower Little River-Saluda River',
  barrierType: 'dams',
  lat: 34.20447326183114,
  lon: -81.7414140701294,
  hasnetwork: true,
}

const { id, name, upnetid = Infinity, countyname, State, lat, lon } = barrier

const TestExportPage = () => {
  const [{ center, bounds, attribution, hasError, isPending }, setState] =
    useState({
      attribution: basemapAttribution['light-v9'],
      center: initCenter,
      bounds: initBounds,
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
      <BarrierReport
        map={mapImage}
        scale={scale}
        // FIXME:
        // scale={{
        //   width: 85,
        //   label: '500 ft',
        // }}
        attribution={attribution}
        locatorMap={locatorMapImage}
        barrierType={barrierType}
        barrier={barrier}
      />
    )
      .toBlob()
      .then((blob) => {
        setState((prevState) => ({
          ...prevState,
          isPending: false,
          hasError: false,
        }))
        saveAs(blob, `${id}_barrier_report.pdf`)
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

        <Header
          name={name}
          county={countyname}
          state={State}
          lat={lat}
          lon={lon}
        />

        {/* <Flex
          sx={{
            width: '100%',
            height: '200px',
            bg: 'grey.1',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            zIndex: 1,
          }}
        >
          ... map goes here ...
          <Box
            sx={{
              position: 'absolute',
              bottom: '10px',
              right: '10px',
              width: '85px',
              fontSize: '10px',
              color: '#333',
              border: '2px solid #333',
              borderTopWidth: 0,
              bg: 'rgba(255,255,255, 0.75)',
              px: '5px',
              py: '2px',
            }}
          >
            500 ft
          </Box>
        </Flex>

        <MapAttribution attribution={attribution} />

        <Flex sx={{ mt: '2rem' }}>
          <Flex
            sx={{
              flex: '0 0 auto',
              width: '200px',
              height: '200px',
              bg: 'grey.1',
              mr: '2rem',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            ... locator map ...
          </Flex>

          <Legend barrierType={barrierType} name={name} />
        </Flex> */}

        <ExportMap
          barrierID={id}
          networkID={upnetid}
          center={initCenter}
          zoom={initZoom}
          barrierType={barrierType}
          onCreateMap={handleCreateExportMap}
          onUpdateBasemap={handleUpdateBasemap}
        />

        <MapAttribution attribution={attribution} />

        <Flex sx={{ mt: '2rem' }}>
          <Box sx={{ flex: '0 0 auto', mr: '2rem' }}>
            <LocatorMap
              center={center}
              zoom={5}
              bounds={bounds}
              onCreateMap={handleCreateLocatorMap}
            />
          </Box>
          <Legend barrierType={barrierType} name={name} />
        </Flex>

        <Flex sx={{ justifyContent: 'space-between', mt: '3rem' }}>
          <Box sx={{ flex: '1 1 auto', width: '50%', mr: '2rem' }}>
            <Location {...barrier} />
          </Box>
          <Box sx={{ flex: '1 1 auto', width: '50%' }}>
            <Construction {...barrier} />
          </Box>
        </Flex>

        <Flex sx={{ justifyContent: 'space-between', mt: '3rem' }}>
          <Box sx={{ flex: '1 1 auto', width: '50%', mr: '2rem' }}>
            <Network {...barrier} />
          </Box>
          <Box sx={{ flex: '1 1 auto', width: '50%' }}>
            <Scores barrierType={barrierType} {...barrier} />
          </Box>
        </Flex>

        <Box sx={{ mt: '3rem' }}>
          <Species {...barrier} />
        </Box>

        <Box sx={{ mt: '3rem' }}>
          <Feasibility {...barrier} />
        </Box>

        <Box sx={{ mt: '3rem' }}>
          <IDInfo {...barrier} />
        </Box>

        <Box sx={{ mt: '3rem' }}>
          <Contact barrierType={barrierType} {...barrier} />
        </Box>

        <Box sx={{ mt: '2rem' }}>
          <Credits />
        </Box>
      </Container>
    </Box>
  )
}

export default TestExportPage
