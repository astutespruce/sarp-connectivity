import React, { useState } from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import { LocationPropType } from "../../CustomPropTypes"
import * as actions from "../../actions/map"

const LatLong = ({ location, setLocation }) => {
    const hasGeolocation = navigator && "geolocation" in navigator
    const { latitude: lat = "", longitude: long = "" } = location

    const [isOpen, setIsOpen] = useState(false)
    const [latitude, setLatitude] = useState(lat)
    const [isLatValid, setIsLatValid] = useState(true)
    const [longitude, setLongitude] = useState(long)
    const [isLongValid, setIsLongValid] = useState(true)
    const [isLocationPending, setIsLocationPending] = useState(false)

    const handleLatitudeChange = ({ target: { value } }) => {
        setLatitude(value)
        setIsLatValid(value === "" || Math.abs(parseFloat(value)) < 89)
    }
    const handleLongitudeChange = ({ target: { value } }) => {
        setLongitude(value)
        setIsLongValid(value === "" || Math.abs(parseFloat(value)) <= 180)
    }

    const handleSetLocation = () => {
        setLocation({
            latitude: parseFloat(latitude),
            longitude: parseFloat(longitude),
            timestamp: new Date().getTime()
        })
        setIsOpen(false)
    }

    const handleClear = () => {
        setLatitude("")
        setLongitude("")
        setIsLatValid(true)
        setIsLongValid(true)
        setIsOpen(false)
        setLocation({})
    }

    // TODO: spinner and error handling
    const handleGetMyLocation = () => {
        // set spinner
        setIsLocationPending(true)
        setIsOpen(false)
        navigator.geolocation.getCurrentPosition(
            ({ coords }) => {
                setLatitude(coords.latitude)
                setLongitude(coords.longitude)
                setIsLatValid(true)
                setIsLongValid(true)
                setLocation({
                    latitude: coords.latitude,
                    longitude: coords.longitude,
                    timestamp: new Date().getTime()
                })
                setIsLocationPending(false)
            },
            error => {
                console.error(error)
                setIsLocationPending(false)
            },
            {
                enableHighAccuracy: false,
                maximumAge: 0,
                timeout: 6000
            }
        )
    }

    return (
        <div className={`map-control map-control-lat-long ${isOpen ? "is-open" : ""}`}>
            <div
                className={`fas fa-crosshairs is-size-5 map-control-toggle ${isLocationPending ? "fa-spin" : ""}`}
                onClick={() => setIsOpen(!isOpen)}
                title="Go to latitude / longitude"
            />
            {isOpen ? (
                <>
                    <span className="map-control-header is-size-6">Go to latitude / longitude</span>
                    <div className="map-control-form">
                        <div className="flex-container flex-justify-end map-control-form-row">
                            <label className="is-size-6 has-text-grey">
                                Latitude:&nbsp;
                                <input
                                    type="number"
                                    onChange={handleLatitudeChange}
                                    className={`is-size-6 ${!isLatValid ? "invalid" : ""}`}
                                    value={latitude}
                                    style={{ width: 120 }}
                                />
                            </label>
                        </div>

                        <div className="flex-container flex-justify-end map-control-form-row">
                            <label className="is-size-6 has-text-grey">
                                Longitude:&nbsp;
                                <input
                                    type="number"
                                    onChange={handleLongitudeChange}
                                    className={`is-size-6 ${!isLongValid ? "invalid" : ""}`}
                                    value={longitude}
                                    style={{ width: 120 }}
                                />
                            </label>
                        </div>

                        <div className="flex-container flex-justify-end map-control-form-row">
                            {hasGeolocation ? (
                                <button type="button" className="button is-small link" onClick={handleGetMyLocation}>
                                    <i className="fas fa-location-arrow" />
                                    &nbsp; use my location
                                </button>
                            ) : null}
                            <button type="button" className="button is-small is-danger" onClick={handleClear}>
                                clear
                            </button>
                            <button
                                type="button"
                                className="button is-small is-info"
                                disabled={!isLatValid || !isLongValid || latitude === "" || longitude === ""}
                                onClick={() => handleSetLocation(latitude, longitude)}
                            >
                                GO
                            </button>
                        </div>
                    </div>
                </>
            ) : null}
        </div>
    )
}

LatLong.propTypes = {
    location: LocationPropType,
    setLocation: PropTypes.func.isRequired
}

LatLong.defaultProps = {
    location: {
        latitude: "",
        longitude: "",
        timestamp: 0
    }
}

const mapStateToProps = globalState => {
    const state = globalState.get("map")

    return {
        location: state.get("location").toJS()
    }
}

export default connect(
    mapStateToProps,
    actions
)(LatLong)
