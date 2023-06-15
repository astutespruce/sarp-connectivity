import React, {
  useCallback,
  useState,
  useEffect,
  useLayoutEffect,
  useRef,
} from 'react'
import PropTypes from 'prop-types'
import { CaretRight, CaretDown } from '@emotion-icons/fa-solid'
import { Box, Flex } from 'theme-ui'

// exclude Mapbox GL from babel transpilation per https://docs.mapbox.com/mapbox-gl-js/guides/migrate-to-v2/
/* eslint-disable-next-line */
import mapboxgl from '!mapbox-gl'

/* eslint-disable-next-line import/order */
import { hasWindow } from 'util/dom'
import { useIsEqualEffect } from 'util/hooks'

import BarrierSearch from './BarrierSearch'
import PlacenameSearch from './PlacenameSearch'
import LatLon from './LatLon'

const controlCSS = {
  alignItems: 'center',
  justifyContent: 'center',
  position: 'absolute',
  padding: '6px',
  color: 'grey.9',
  bg: '#FFF',
  pointerEvents: 'auto',
  borderRadius: '0.25rem',
  boxShadow: '0 0 0 2px rgba(0,0,0,.1)',
}

const FindLocation = ({ map }) => {
  const isMountedRef = useRef(false)
  const markerRef = useRef(null)
  const barrierInputRef = useRef(null)
  const placenameInputRef = useRef(null)
  const latLonInputRef = useRef(null)

  const [{ mode, showOptions, isFocused, location }, setState] = useState({
    mode: 'barrier',
    showOptions: false,
    isFocused: false,
    location: null,
    showPlacenameResults: true,
  })

  useIsEqualEffect(() => {
    if (!map) {
      return
    }

    const { current: marker } = markerRef

    console.log('location updated', location)
    if (location === null) {
      if (marker) {
        marker.remove()
      }
      markerRef.current = null
    } else {
      const { latitude, longitude } = location
      map.jumpTo({ center: [longitude, latitude], zoom: 14 })
      if (!marker) {
        markerRef.current = new mapboxgl.Marker()
          .setLngLat([longitude, latitude])
          .addTo(map)
      } else {
        markerRef.current.setLngLat([longitude, latitude])
      }
    }
  }, [map, location])

  const toggleShowOptions = useCallback((e) => {
    e.stopPropagation()

    setState(({ showOptions: prevShowOptions, ...prevState }) => ({
      ...prevState,
      showOptions: !prevShowOptions,
      isFocused: true,
    }))
  }, [])

  const handleFocus = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      showOptions: false,
      isFocused: true,
    }))
  }, [])

  const handleSubmit = useCallback((newLocation) => {
    setState((prevState) => ({
      ...prevState,
      isFocused: false,
      location: newLocation,
    }))
  }, [])

  const handleReset = useCallback(() => {
    setState((prevState) => ({
      ...prevState,
      location: null,
      isFocused: false,
    }))
  }, [])

  const setBarrierMode = useCallback((e) => {
    e.stopPropagation()

    if (barrierInputRef.current) {
      barrierInputRef.current.focus()
    }

    setState(({ mode: prevMode, ...prevState }) => ({
      ...prevState,
      mode: 'barrier',
      showOptions: false,
      isFocused: true,
    }))
  }, [])

  const setPlacenameMode = useCallback((e) => {
    e.stopPropagation()

    if (placenameInputRef.current) {
      placenameInputRef.current.focus()
    }

    setState(({ mode: prevMode, ...prevState }) => ({
      ...prevState,
      mode: 'placename',
      showOptions: false,
      isFocused: true,
    }))
  }, [])

  const setLatLonMode = useCallback((e) => {
    e.stopPropagation()

    if (latLonInputRef.current) {
      latLonInputRef.current.focus()
    }

    setState((prevState) => ({
      ...prevState,
      mode: 'latlon',
      showOptions: false,
      isFocused: true,
    }))
  }, [])

  useLayoutEffect(() => {
    // skip on first mount
    if (!isMountedRef.current) {
      isMountedRef.current = true
      return
    }

    if (mode === 'placename') {
      if (placenameInputRef.current) {
        placenameInputRef.current.focus()
      }
    } else if (latLonInputRef.current) {
      latLonInputRef.current.focus()
    }
  }, [mode])

  // prevent click from calling window click handler
  const handleClick = useCallback((e) => e.stopPropagation(), [])

  // add event listener to the window
  useEffect(() => {
    const handleWindowClick = () => {
      if (isFocused) {
        setState((prevState) => ({
          ...prevState,
          showOptions: false,
          isFocused: false,
        }))
      }
    }

    if (hasWindow) {
      document.addEventListener('click', handleWindowClick)
    }

    return () => {
      if (hasWindow) {
        document.removeEventListener('click', handleWindowClick)
      }
    }
  }, [isFocused])

  return (
    <>
      <Box
        onClick={handleClick}
        sx={{
          ...controlCSS,
          zIndex: 2001,
          top: '6px',
          right: '10px',
          overflow: 'hidden',
          userSelect: 'none',
          width: isFocused || showOptions ? '290px' : '160px',
        }}
      >
        <Flex sx={{ alignItems: 'flex-start' }}>
          <Box
            onClick={toggleShowOptions}
            sx={{ flex: '0 0 auto', cursor: 'pointer', color: 'grey.8' }}
          >
            {showOptions ? (
              <CaretDown size="1.5em" />
            ) : (
              <CaretRight size="1.5em" style={{ marginTop: '0.2rem' }} />
            )}
          </Box>
          <Box sx={{ flex: '1 1 auto', fontSize: 0 }}>
            <Box
              sx={{
                display: mode === 'barrier' ? 'block' : 'none',
              }}
            >
              <BarrierSearch
                ref={barrierInputRef}
                isFocused={isFocused && !showOptions}
                onSubmit={handleSubmit}
                onReset={handleReset}
                onFocus={handleFocus}
              />
            </Box>
            <Box
              sx={{
                display: mode === 'placename' ? 'block' : 'none',
              }}
            >
              <PlacenameSearch
                ref={placenameInputRef}
                isFocused={isFocused && !showOptions}
                onSubmit={handleSubmit}
                onReset={handleReset}
                onFocus={handleFocus}
              />
            </Box>

            <Box
              sx={{
                display: mode === 'latlon' ? 'block' : 'none',
              }}
            >
              <LatLon
                ref={latLonInputRef}
                isFocused={isFocused}
                onSubmit={handleSubmit}
                onReset={handleReset}
                onFocus={handleFocus}
              />
            </Box>
          </Box>
        </Flex>

        {showOptions ? (
          <Box
            sx={{
              mt: '0.25rem',
              pt: '0.25rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.3',
              fontSize: 1,
              lineHeight: 1,
              '& > div': {
                p: '0.25rem',
                cursor: 'pointer',
                '&:hover': {
                  bg: 'grey.0',
                },
              },
            }}
          >
            <Box onClick={setBarrierMode}>Find a barrier by name or ID</Box>
            <Box onClick={setPlacenameMode}>
              Find a place by name or address
            </Box>
            <Box onClick={setLatLonMode}>Find by latitude & longitude</Box>
          </Box>
        ) : null}
      </Box>
    </>
  )
}

FindLocation.propTypes = {
  map: PropTypes.object,
}

FindLocation.defaultProps = {
  map: null,
}

export default FindLocation
