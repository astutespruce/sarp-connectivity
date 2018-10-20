import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import * as actions from "../../actions"
import { FeaturePropType } from "../../CustomPropTypes"

import SummaryMap from "../Map/SummaryMap"
import Sidebar from "../Map/Sidebar"

const Summary = ({ system, selectedFeature }) => (
    // const handleBackClick = () => (unit !== null ? setUnit(null) : goBack())
    <React.Fragment>
        <Sidebar>
            {system !== null && (
                <React.Fragment>
                    {/* <div className="section">
                            <button type="button" onClick={handleBackClick}>
                                Go back
                            </button>
                        </div> */}
                    <h3>Current system is: {system} </h3>
                    {selectedFeature !== null && <h3>Selected: {selectedFeature.id}</h3>}
                </React.Fragment>
            )}
        </Sidebar>
        <div id="MapContainer">
            <SummaryMap />
        </div>
    </React.Fragment>
)

Summary.propTypes = {
    system: PropTypes.string,
    selectedFeature: FeaturePropType,

    setSystem: PropTypes.func.isRequired,
    selectFeature: PropTypes.func.isRequired,
    goBack: PropTypes.func.isRequired
}

Summary.defaultProps = {
    system: null,
    selectedFeature: null
}

const mapStateToProps = state => ({ system: state.get("system"), selectedFeature: state.get("selectedFeature") })

export default connect(
    mapStateToProps,
    actions
)(Summary)
