import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import * as actions from "../../actions"
import Map from "../Map"
import Sidebar from "../Map/Sidebar"

const Summary = ({ system, level, unit, setSystem, setUnit, goBack }) => {
    const handleBackClick = () => (unit !== null ? setUnit(null) : goBack())
    return (
        <React.Fragment>
            <Sidebar>
                {system === null ? (
                    <React.Fragment>
                        <h3>Which unit system?</h3>
                        <div className="section">
                            <button className="button" type="button" onClick={() => setSystem("HUC")}>
                                Watersheds
                            </button>
                        </div>

                        <div className="section">
                            <button className="button" type="button" onClick={() => setSystem("ecoregion")}>
                                Ecoregions
                            </button>
                        </div>
                    </React.Fragment>
                ) : (
                    <React.Fragment>
                        <div className="section">
                            <button type="button" onClick={handleBackClick}>
                                Go back
                            </button>
                        </div>
                        <h3>
                            Current system is: {system} {level}{" "}
                        </h3>
                    </React.Fragment>
                )}
            </Sidebar>
            <div id="MapContainer">
                <Map view="summary" />
            </div>
        </React.Fragment>
    )
}

Summary.propTypes = {
    system: PropTypes.string,
    level: PropTypes.string,
    unit: PropTypes.string,
    setSystem: PropTypes.func.isRequired,
    setUnit: PropTypes.func.isRequired,
    goBack: PropTypes.func.isRequired
}

Summary.defaultProps = {
    system: null,
    level: null,
    unit: null
}

const mapStateToProps = state => ({ system: state.get("system"), level: state.get("level"), unit: state.get("unit") })

export default connect(
    mapStateToProps,
    actions
)(Summary)
