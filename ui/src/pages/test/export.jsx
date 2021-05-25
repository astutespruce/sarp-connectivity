import React, { useState, useCallback, useRef } from 'react'
import { Box, Container, Flex, Button } from 'theme-ui'
import { saveAs } from 'file-saver'
import { PDFViewer } from '@react-pdf/renderer'

import { BarrierReport } from 'components/Report'
import { ExportMap, LocatorMap, mapToBlob, mapToDataURL } from 'components/Map'

const initBounds = [
  -81.75491755391782, 34.202167532091835, -81.71679157217531,
  34.225793798992214,
]
const barrierType = 'dams'
const initZoom = 13.5
const initCenter = [-81.73324540257454, 34.214985614638195]

const barrierID = 109572
const networkID = 3014872

const TestExportPage = () => {
  const [{ center, bounds, maps }, setState] = useState({
    center: initCenter,
    bounds: initBounds,
    maps: null,
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

  const handleExport = async () => {
    const [mapImage, locatorMapImage] = await Promise.all([
      //   mapToBlob(exportMapRef.current),
      //   mapToBlob(locatorMapRef.current),
      mapToDataURL(exportMapRef.current),
      mapToDataURL(locatorMapRef.current),
    ])

    // console.log('mapImage', mapImage, locatorMapImage)

    setState((prevState) => ({
      ...prevState,
      maps: {
        main: mapImage,
        locator: locatorMapImage,
      },
    }))

    // saveAs(mapImage, 'map.png')
    // saveAs(locatorMapImage, 'locator.png')

    // possibly need this instead of blob
    // renderMap.getCanvas().toDataURL('image/png')

    // TODO: attribution and legend
  }

  return (
    <Box sx={{ overflow: 'auto', height: '100%' }}>
      {maps ? (
        <PDFViewer width="100%" height="100%">
          <BarrierReport
            name="John Wilson Dam"
            county="Newberry County"
            state="South Carolina"
            map={maps.main}
            locatorMap={maps.locator}
          />
        </PDFViewer>
      ) : (
        <Container sx={{ width: '800px', pb: '4rem', height: '100%' }}>
          <Flex sx={{ justifyContent: 'flex-end', mb: '1rem' }}>
            <Button onClick={handleExport}>Export to PDF</Button>
          </Flex>

          <ExportMap
            barrierID={barrierID}
            networkID={networkID}
            center={initCenter}
            zoom={initZoom}
            barrierType={barrierType}
            onCreateMap={handleCreateExportMap}
          />

          <Box sx={{ mt: '2rem' }}>
            <LocatorMap
              center={center}
              zoom={5}
              bounds={bounds}
              onCreateMap={handleCreateLocatorMap}
            />
          </Box>
        </Container>
      )}
    </Box>
  )
}

export default TestExportPage
