import React, { useState, useRef, memo } from 'react'
import PropTypes from 'prop-types'
import { Crosshairs, LocationArrow } from '@emotion-icons/fa-solid'
import mapboxgl from 'mapbox-gl'
import { Box, Button, Input, Flex, Spinner, Text } from 'theme-ui'

import { hasGeolocation } from 'util/dom'

const navigatorOptions = {
  enableHighAccuracy: false,
  maximumAge: 0,
  timeout: 6000,
}

const controlCSS = {
  position: 'absolute',
  top: '110px',
  right: '10px',
  lineHeight: 1,
  bg: '#FFF',
  border: 'none',
  borderRadius: '4px',
  boxShadow: '0 0 0 2px rgba(0,0,0,0.1)',
  padding: '7px',
  zIndex: 2000,
}

const GoToLocation = ({ map }) => {
  const markerRef = useRef(null)
  const [state, setState] = useState({
    isOpen: false,
    isPending: false,
    lat: '',
    lon: '',
    isLatValid: true,
    isLonValid: true,
  })

  const { isOpen, isPending, lat, lon, isLatValid, isLonValid } = state

  const handleLatitudeChange = ({ target: { value } }) => {
    setState((prevState) => ({
      ...prevState,
      lat: value,
      isLatValid: value === '' || Math.abs(parseFloat(value)) < 89,
    }))
  }

  const handleLongitudeChange = ({ target: { value } }) => {
    setState((prevState) => ({
      ...prevState,
      lon: value,
      isLonValid: value === '' || Math.abs(parseFloat(value)) <= 180,
    }))
  }

  const handleSetLocation = () => {
    setLocation({
      latitude: parseFloat(lat),
      longitude: parseFloat(lon),
      timestamp: new Date().getTime(),
    })

    setState((prevState) => ({
      ...prevState,
      isOpen: false,
    }))
  }

  const handleClear = () => {
    setState((prevState) => ({
      ...prevState,
      isOpen: false,
      lat: '',
      lon: '',
      isLatValid: true,
      isLonValid: true,
    }))

    setLocation({
      latitude: null,
      longitude: null,
    })
  }

  const handleToggle = () => {
    setState((prevState) => ({
      ...prevState,
      isOpen: !prevState.isOpen,
    }))
  }

  const handleGetMyLocation = () => {
    setState({
      ...state,
      isPending: true,
      isOpen: false,
    })
    navigator.geolocation.getCurrentPosition(
      ({ coords: { latitude, longitude } }) => {
        setState({
          ...state,
          isPending: false,
          isOpen: false,
          lat: latitude,
          lon: longitude,
          isLatValid: true,
          isLonValid: true,
        })
        setLocation({
          latitude,
          longitude,
          timestamp: new Date().getTime(),
        })
      },
      (error) => {
        console.error(error)
        setState((prevState) => ({
          ...prevState,
          isPending: false,
        }))
      },
      navigatorOptions
    )
  }

  const setLocation = ({ latitude, longitude }) => {
    const { current: marker } = markerRef

    if (latitude === null || longitude === null) {
      if (marker) {
        marker.remove()
      }

      markerRef.current = null
    } else {
      map.flyTo({ center: [longitude, latitude], zoom: 9 })
      if (!marker) {
        markerRef.current = new mapboxgl.Marker()
          .setLngLat([longitude, latitude])
          .addTo(map)
      } else {
        markerRef.current.setLngLat([longitude, latitude])
      }
    }
  }

  if (isPending) {
    return (
      <Box sx={controlCSS}>
        <Spinner
          size="1em"
          onClick={handleToggle}
          title="Go to latitude / longitude"
        />
      </Box>
    )
  }

  if (!isOpen) {
    return (
      <Box
        sx={{
          ...controlCSS,
          mt: '1px',
          cursor: 'pointer',
          '&:hover': {
            bg: '#EEE',
          },
        }}
        onClick={handleToggle}
        title="Go to latitude / longitude"
      >
        <Crosshairs size="1em" />
      </Box>
    )
  }

  const isDisabled = !isLatValid || !isLonValid || lat === '' || lon === ''

  return (
    <Box
      sx={{
        ...controlCSS,
        zIndex: 20000,
        border: '1px solid #AAA',
        boxShadow: '1px 1px 8px #333',
      }}
    >
      <Flex sx={{ alignItems: 'center' }}>
        <Box sx={{ flex: '0 0 auto' }} onClick={handleToggle}>
          <Crosshairs size="1em" />
        </Box>

        <Text
          onClick={handleToggle}
          sx={{
            ml: '0.5em',
            mr: '1rem',
            flex: '1 1 auto',
            fontWeight: 'bold',
            fontSize: 1,
            cursor: 'pointer',
          }}
        >
          Go to latitude / longitude
        </Text>

        <Button
          variant="close"
          sx={{ fontSize: '0.8rem', height: '0.9rem', width: '0.9rem' }}
          onClick={handleToggle}
        >
          &#10006;
        </Button>
      </Flex>

      <Box sx={{ mt: '1rem' }}>
        <Flex
          sx={{
            justifyContent: 'flex-end',
            alignItems: 'center',
          }}
        >
          <Text variant="help">Latitude:&nbsp;</Text>
          <Input
            type="number"
            onChange={handleLatitudeChange}
            value={lat}
            variant={isLatValid ? 'input-default' : 'input-invalid'}
            sx={{ width: '120px', flex: '0 0 auto', ml: '1rem' }}
          />
        </Flex>

        <Flex
          sx={{
            justifyContent: 'flex-end',
            alignItems: 'center',
            mt: '0.5rem',
          }}
        >
          <Text variant="help">Longitude:&nbsp;</Text>
          <Input
            type="number"
            onChange={handleLongitudeChange}
            value={lon}
            variant={isLonValid ? 'input-default' : 'input-invalid'}
            sx={{ width: '120px', flex: '0 0 auto', ml: '1rem' }}
          />
        </Flex>

        <Flex
          sx={{
            justifyContent: 'flex-end',
            alignItems: 'center',
            mt: '0.5rem',
            fontSize: 1,
            button: {
              px: '0.5em',
              py: '0.25em',
              '&:not(:first-of-type)': {
                ml: '0.5rem',
              },
            },
          }}
        >
          {hasGeolocation ? (
            <Button
              onClick={handleGetMyLocation}
              sx={{
                border: 'none',
                color: 'link',
                backgroundColor: 'transparent !important',
                mr: '1rem',
              }}
            >
              <LocationArrow size="1em" />
              &nbsp; use my location
            </Button>
          ) : null}
          <Button variant="warning" onClick={handleClear}>
            clear
          </Button>
          <Button
            disabled={isDisabled}
            variant={isDisabled ? 'disabled' : 'primary'}
            onClick={handleSetLocation}
          >
            GO
          </Button>
        </Flex>
      </Box>
    </Box>
  )
}

GoToLocation.propTypes = {
  map: PropTypes.object.isRequired,
}

export default GoToLocation //memo(GoToLocation)
