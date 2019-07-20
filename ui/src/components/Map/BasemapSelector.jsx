import React, { useState, useRef, useMemo, memo } from 'react'
import PropTypes from 'prop-types'

import styled, { css, themeGet } from 'style'
import { siteMetadata } from '../../../gatsby-config'

const { mapboxToken } = siteMetadata

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

  &:hover {
    box-shadow: 0 1px 5px rgba(0, 0, 0, 1);
    border-color: #eee;
  }

  ${({ size }) => css`
    width: ${size};
    height: ${size};
    border-radius: ${size};
  `}
`

const BasemapSelector = ({
  map,
  defaultStyle,
  basemaps,
  tile: { z, x, y },
  size,
}) => {
  const [isOpen, setIsOpen] = useState(false)

  // memoize construction of options to avoid doing this on every render
  const options = useMemo(() => {
    const basemapOptions = Object.entries(basemaps).map(([group, layers]) => {
      layers.forEach(({ id, source, ...rest }) => {
        map.addSource(id, source)
        map.addLayer({
          ...rest,
          id,
          source: id,
        })
      })

      const { id, source } = layers[0]
      return {
        id,
        src: source.tiles[0]
          .replace('{z}', z)
          .replace('{x}', x)
          .replace('{y}', y),
        layers: layers.map(({ id: layerId }) => layerId),
      }
    })

    return [
      {
        id: 'grey',
        src: `https://api.mapbox.com/styles/v1/mapbox/${defaultStyle}/tiles/256/${z}/${x}/${y}?access_token=${mapboxToken}`,
        layers: [],
      },
    ].concat(basemapOptions)
  }, [basemaps, defaultStyle, map, x, y, z])

  const [basemap, setBasemap] = useState(options[0])

  const handleBasemapClick = newBasemap => {
    setIsOpen(false)

    if (newBasemap.id === basemap.id) return

    setBasemap(prevBasemap => {
      prevBasemap.layers.forEach(layer => {
        map.setLayoutProperty(layer, 'visibility', 'none')
      })

      newBasemap.layers.forEach(layer => {
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
              size={size}
              src={nextBasemap.src}
              onClick={() => handleBasemapClick(nextBasemap)}
            />
          </BasemapContainer>
          {options
            .filter(({ id }) => id !== nextBasemap.id)
            .map(altBasemap => (
              <BasemapContainer key={altBasemap.id}>
                <Label>{altBasemap.id}</Label>
                <Basemap
                  isActive={altBasemap.id === basemap.id}
                  size={size}
                  src={altBasemap.src}
                  onClick={() => handleBasemapClick(altBasemap)}
                />
              </BasemapContainer>
            ))}
        </>
      ) : (
        <Basemap
          size={size}
          src={nextBasemap.src}
          onClick={() => handleBasemapClick(nextBasemap)}
        />
      )}
    </Wrapper>
  )
}

BasemapSelector.propTypes = {
  map: PropTypes.object.isRequired,
  defaultStyle: PropTypes.string.isRequired,
  basemaps: PropTypes.objectOf(
    PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
        source: PropTypes.object.isRequired,
      })
    )
  ).isRequired,
  tile: PropTypes.shape({
    x: PropTypes.number.isRequired,
    y: PropTypes.number.isRequired,
    z: PropTypes.number.isRequired,
  }),
  size: PropTypes.string,
}

BasemapSelector.defaultProps = {
  tile: {
    x: 0,
    y: 0,
    z: 0,
  },
  size: '64px',
}

export default memo(BasemapSelector)
