import React, { useState, memo, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Box } from 'theme-ui'

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
  }, [map])

  return (
    lat !== undefined &&
    lng !== undefined && (
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: '110px',
          py: '4px',
          px: '8px',
          zIndex: 2000,
          bg: 'rgba(255,255,255,0.5)',
          fontSize: '0.75rem',
        }}
      >
        {Math.round(lat * 100000) / 100000}° N,&nbsp;
        {Math.round(lng * 100000) / 100000}° E
      </Box>
    )
  )
}

Coords.propTypes = {
  map: PropTypes.object.isRequired,
}

export default memo(Coords)
