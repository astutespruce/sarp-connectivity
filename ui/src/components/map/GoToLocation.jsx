import React, { useState, useRef, memo } from 'react'
import PropTypes from 'prop-types'
import { FaCrosshairs, FaLocationArrow, FaTimesCircle } from 'react-icons/fa'
import mapboxgl from 'mapbox-gl'

import { Box, Flex } from 'components/Grid'
import { Button as BaseButton } from 'components/Button'
import { hasGeolocation } from 'util/dom'
import styled, { themeGet, keyframes, css } from 'style'
import { MapControlWrapper } from './styles'

const navigatorOptions = {
  enableHighAccuracy: false,
  maximumAge: 0,
  timeout: 6000,
}

const Wrapper = styled(MapControlWrapper)`
  top: 110px;
  right: 10px;
  line-height: 1;
  background-color: ${({ isOpen }) => (isOpen ? '#eee' : '#fff')};
`

const Header = styled.span`
  margin: 0 0.5em;
  font-weight: bold;
  font-size: 0.9em;
  display: inline-block;
  vertical-align: top;
  margin-top: 4px;
  cursor: pointer;
`

const Icon = styled(FaCrosshairs)`
  width: 1em;
  height: 1em;
  margin-top: 1px;
  cursor: pointer;
`

const spin = keyframes`
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
`

const PendingIcon = styled(Icon)`
  animation: ${spin} 2s linear infinite;
`

const ArrowIcon = styled(FaLocationArrow)`
  width: 1em;
  height: 1em;
`

const CloseIcon = styled(FaTimesCircle)`
  width: 1em;
  height: 1em;
  color: ${themeGet('colors.grey.500')};
  cursor: pointer;

  &:hover {
    color: ${themeGet('colors.grey.900')};
  }
`

const Form = styled(Box).attrs({ p: '0.5rem' })``

const Row = styled(Flex).attrs({
  justifyContent: 'flex-end',
  alignItems: 'center',
})`
  &:not(:first-child) {
    margin-top: 0.5rem;
  }
`

const Input = styled.input.attrs({
  type: 'number',
})`
  width: 120px;
  font-size: 0.8em;
  outline: none;
  margin-left: 0.25em;
  padding: 0.25em;
  border-radius: 0.25em;

  border: 1px solid ${themeGet('colors.grey.500')};
  &:focus {
    border-color: ${themeGet('colors.primary.500')};
  }

  ${({ isValid }) =>
    !isValid &&
    css`
      color: #ea1b00;
      border-color: #ea1b00 !important;
    `}
`

const Label = styled.span`
  color: ${themeGet('colors.grey.700')};
  font-size: 0.9em;
`

const Button = styled(BaseButton)`
  font-size: 0.8em;
  padding: 0.25em 0.5em;
  font-weight: normal;

  &:not(:first-child) {
    margin-left: 0.5em;
  }
`

const LinkButton = styled(Button)`
  color: ${themeGet('colors.link')};
  border: none;
  background: none;
`

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
    setState(prevState => ({
      ...prevState,
      lat: value,
      isLatValid: value === '' || Math.abs(parseFloat(value)) < 89,
    }))
  }

  const handleLongitudeChange = ({ target: { value } }) => {
    setState(prevState => ({
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

    setState(prevState => ({
      ...prevState,
      isOpen: false,
    }))
  }

  const handleClear = () => {
    setState(prevState => ({
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
    setState(prevState => ({
      ...prevState,
      isOpen: !prevState.isOpen,
    }))
  }

  // TODO: spinner and error handling
  const handleGetMyLocation = () => {
    // set spinner
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
      error => {
        console.error(error)
        setState(prevState => ({
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

  return (
    <Wrapper isOpen={isOpen}>
      {isPending ? (
        <PendingIcon
          onClick={handleToggle}
          title="Go to latitude / longitude"
        />
      ) : (
        <Icon onClick={handleToggle} title="Go to latitude / longitude" />
      )}

      {isOpen ? (
        <>
          <Header onClick={handleToggle}>Go to latitude / longitude</Header>
          <CloseIcon onClick={handleToggle} />
          <Form>
            <Row>
              <Label>Latitude:&nbsp;</Label>
              <Input
                onChange={handleLatitudeChange}
                className={`is-size-6 ${!isLatValid ? 'invalid' : ''}`}
                value={lat}
                isValid={isLatValid}
              />
            </Row>
            <Row>
              <Label>Longitude:&nbsp;</Label>
              <Input
                onChange={handleLongitudeChange}
                className={`is-size-6 ${!isLonValid ? 'invalid' : ''}`}
                value={lon}
                isValid={isLonValid}
              />
            </Row>

            <Row>
              {hasGeolocation ? (
                <LinkButton onClick={handleGetMyLocation}>
                  <ArrowIcon />
                  &nbsp; use my location
                </LinkButton>
              ) : null}
              <Button warning onClick={handleClear}>
                clear
              </Button>
              <Button
                primary
                disabled={
                  !isLatValid || !isLonValid || lat === '' || lon === ''
                }
                onClick={handleSetLocation}
              >
                GO
              </Button>
            </Row>
          </Form>
        </>
      ) : null}
    </Wrapper>
  )
}

GoToLocation.propTypes = {
  map: PropTypes.object.isRequired,
  // setLocation: PropTypes.func.isRequired,
}

export default memo(GoToLocation)
