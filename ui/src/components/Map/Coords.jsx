import React, { useState, memo, useEffect } from 'react'
import PropTypes from 'prop-types'

import styled from 'style'

const Wrapper = styled.div`
  position: absolute;
  bottom: 0px;
  left: 110px;
  padding: 4px 8px;
  z-index: 2000;
  background: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
`

const Coords = ({ map }) => {
  const [{ lat, lng }, setCoords] = useState({})

  useEffect(() => {
    // Track mouse cursor and display coordinates
    map.on('mousemove', ({ lngLat }) => {
      setCoords(lngLat)
    })

    map.on('mouseout', () => {
      setCoords({})
    })
  }, [])

  return (
    lat !== undefined &&
    lng !== undefined && (
      <Wrapper>
        {Math.round(lat * 100000) / 100000}° N,&nbsp;
        {Math.round(lng * 100000) / 100000}° E
      </Wrapper>
    )
  )
}

Coords.propTypes = {
  map: PropTypes.object.isRequired,
}

export default memo(Coords)
