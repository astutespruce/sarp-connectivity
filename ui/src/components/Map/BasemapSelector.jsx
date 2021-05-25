import React, { useState, useMemo, useEffect, memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Image, Text } from 'theme-ui'

import LightIcon from 'images/light-v9.png'
import StreetsIcon from 'images/esri-streets.jpg'
import TopoIcon from 'images/esri-topo.jpg'
import ImageryIcon from 'images/esri-imagery.jpg'

const icons = {
  'light-v9': LightIcon,
  imagery: ImageryIcon,
  streets: StreetsIcon,
  topo: TopoIcon,
}

const BasemapSelector = ({ map, basemaps, size, bottom, left, onUpdate }) => {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    if (!map) return

    Object.values(basemaps).forEach((layers) => {
      layers.forEach(({ id, source, ...rest }) => {
        // due to the way hot reloading works with the map, this gets called
        // on hot module reload and breaks because layers were already added to the map

        if (!map.getSource(id)) {
          map.addSource(id, source)
        }
        if (!map.getLayer(id)) {
          map.addLayer({
            ...rest,
            id,
            source: id,
          })
        }
      })
    })
  }, [map, basemaps])

  // memoize construction of options to avoid doing this on every render
  const options = useMemo(() => {
    const basemapOptions = Object.values(basemaps).map((layers) => {
      const { id } = layers[0]
      return {
        id,
        src: icons[id],
        layers: layers.map(({ id: layerId }) => layerId),
      }
    })

    return [
      {
        id: 'light-v9',
        src: icons['light-v9'],
        layers: [],
      },
    ].concat(basemapOptions)
  }, [basemaps])

  const [basemap, setBasemap] = useState(options[0])

  const handleBasemapClick = (newBasemap) => {
    setIsOpen(false)

    if (newBasemap.id === basemap.id) return

    setBasemap((prevBasemap) => {
      prevBasemap.layers.forEach((layer) => {
        map.setLayoutProperty(layer, 'visibility', 'none')
      })

      newBasemap.layers.forEach((layer) => {
        map.setLayoutProperty(layer, 'visibility', 'visible')
      })
      return newBasemap
    })

    onUpdate(newBasemap.id)
  }

  const toggleOpen = () => {
    setIsOpen(true)
  }

  const toggleClosed = () => {
    setIsOpen(false)
  }

  const nextBasemap = options.filter(({ id }) => id !== basemap.id)[0]

  return (
    <Box
      onMouseEnter={toggleOpen}
      onMouseLeave={toggleClosed}
      sx={{
        cursor: 'pointer',
        position: 'absolute',
        left,
        bottom,
        zIndex: 999,
      }}
    >
      {isOpen ? (
        <>
          <Box
            sx={{
              display: 'inline-block',
              '&:not(:first-of-type)': {
                ml: '0.25rem',
              },
            }}
          >
            <Text
              sx={{
                fontSize: '0.7rem',
                textAlign: 'center',
                color: 'grey.7',
                mb: '0.25rem',
              }}
            >
              {nextBasemap.id}
            </Text>
            <Image
              variant="basemap"
              src={nextBasemap.src}
              sx={{
                width: size,
                height: size,
              }}
              onClick={() => handleBasemapClick(nextBasemap)}
            />
          </Box>
          {options
            .filter(({ id }) => id !== nextBasemap.id)
            .map((altBasemap) => (
              <Box
                key={altBasemap.id}
                sx={{
                  display: 'inline-block',
                  '&:not(:first-of-type)': {
                    ml: '0.25rem',
                  },
                }}
              >
                <Text
                  sx={{
                    fontSize: '0.7rem',
                    textAlign: 'center',
                    color: 'grey.7',
                    mb: '0.25rem',
                  }}
                >
                  {altBasemap.id}
                </Text>
                <Image
                  variant={
                    altBasemap.id === basemap.id ? 'basemap-active' : 'basemap'
                  }
                  src={altBasemap.src}
                  sx={{
                    width: size,
                    height: size,
                  }}
                  onClick={() => handleBasemapClick(altBasemap)}
                />
              </Box>
            ))}
        </>
      ) : (
        <Image
          variant="basemap"
          src={nextBasemap.src}
          sx={{
            width: size,
            height: size,
          }}
          onClick={() => handleBasemapClick(nextBasemap)}
        />
      )}
    </Box>
  )
}

BasemapSelector.propTypes = {
  map: PropTypes.object.isRequired,
  // NOTE: these must have corresponding images loaded directly in here
  basemaps: PropTypes.objectOf(
    PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
      })
    )
  ).isRequired,
  size: PropTypes.string,
  bottom: PropTypes.string,
  left: PropTypes.string,
  onUpdate: PropTypes.func,
}

BasemapSelector.defaultProps = {
  size: '64px',
  bottom: '24px',
  left: '10px',
  onUpdate: () => {},
}

// Only construct once, when the map boots
export default memo(BasemapSelector)
