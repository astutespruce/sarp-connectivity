import React, { useState, useMemo, useEffect, memo } from 'react'
import PropTypes from 'prop-types'

import styled, { themeGet } from 'style'

import LightIcon from 'images/light-v9.png'
import StreetsIcon from 'images/esri-streets.jpg'
import TopoIcon from 'images/esri-topo.jpg'
import ImageryIcon from 'images/esri-imagery.jpg'

const Wrapper = styled.div`
  cursor: pointer;
  position: absolute;
  left: 10px;
  bottom: 24px;
  z-index: 999;
`

const BasemapContainer = styled.div`
  display: inline-block;
  &:not(:first-child) {
    margin-left: 0.25rem;
  }
`

const Label = styled.div`
  font-size: 0.7rem;
  text-align: center;
  color: ${themeGet('colors.grey.700')};
  margin-bottom: 0.25rem;
`

const Basemap = styled.img`
  box-sizing: border-box;
  border: 2px solid
    ${({ isActive }) => (isActive ? themeGet('colors.highlight.500') : '#fff')};
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.65);
  margin: 0;

  width: 64px;
  height: 64px;
  border-radius: 64px;

  &:hover {
    box-shadow: 0 1px 5px rgba(0, 0, 0, 1);
    border-color: #eee;
  }
`

const icons = {
  'light-v9': LightIcon,
  imagery: ImageryIcon,
  streets: StreetsIcon,
  topo: TopoIcon,
}

const BasemapSelector = ({ map, basemaps }) => {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
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
        id: 'grey',
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
  }

  const toggleOpen = () => {
    setIsOpen(true)
  }

  const toggleClosed = () => {
    setIsOpen(false)
  }

  const nextBasemap = options.filter(({ id }) => id !== basemap.id)[0]

  return (
    <Wrapper onMouseEnter={toggleOpen} onMouseLeave={toggleClosed}>
      {isOpen ? (
        <>
          <BasemapContainer>
            <Label>{nextBasemap.id}</Label>
            <Basemap
              src={nextBasemap.src}
              onClick={() => handleBasemapClick(nextBasemap)}
            />
          </BasemapContainer>
          {options
            .filter(({ id }) => id !== nextBasemap.id)
            .map((altBasemap) => (
              <BasemapContainer key={altBasemap.id}>
                <Label>{altBasemap.id}</Label>
                <Basemap
                  isActive={altBasemap.id === basemap.id}
                  src={altBasemap.src}
                  onClick={() => handleBasemapClick(altBasemap)}
                />
              </BasemapContainer>
            ))}
        </>
      ) : (
        <Basemap
          src={nextBasemap.src}
          onClick={() => handleBasemapClick(nextBasemap)}
        />
      )}
    </Wrapper>
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
}

// Only construct once, when the map boots
export default memo(BasemapSelector)
