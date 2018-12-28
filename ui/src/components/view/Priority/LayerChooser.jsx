import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"

const LayerChooser = ({ setLayer }) => {
    const handleClick = id => () => setLayer(id)

    return (
        <React.Fragment>
            <div id="SidebarContent">
                <h4 className="title is-4">What type of area do you want to select?</h4>
                <p className="has-text-grey">
                    Choose from one of the following types of areas that will best capture your area of interest. You
                    will select specific areas on the next screen.
                </p>
                <div id="SummaryUnitChooser">
                    <h5
                        className="is-size-5"
                        style={{
                            marginTop: "1rem"
                        }}
                    >
                        Administrative unit
                    </h5>
                    <div className="button-group flex-container">
                        <button className="button" type="button" onClick={handleClick("State")}>
                            State
                        </button>
                        <button className="button" type="button" onClick={handleClick("County")}>
                            County
                        </button>
                    </div>
                    <h5
                        className="is-size-5"
                        style={{
                            marginTop: "2rem"
                        }}
                    >
                        Hydrologic unit
                    </h5>
                    <div className="button-group flex-container">
                        <button
                            className="button"
                            type="button"
                            onClick={handleClick("HUC6")}
                            style={{ height: "auto" }}
                        >
                            Basin
                            <br />
                            (HUC6)
                        </button>
                        <button
                            className="button"
                            type="button"
                            onClick={handleClick("HUC8")}
                            style={{ height: "auto" }}
                        >
                            Subbasin
                            <br />
                            (HUC8)
                        </button>
                        <button
                            className="button"
                            type="button"
                            onClick={handleClick("HUC12")}
                            style={{ height: "auto" }}
                        >
                            Subwatershed
                            <br />
                            (HUC12)
                        </button>
                    </div>

                    <h5
                        className="is-size-5"
                        style={{
                            marginTop: "2rem"
                        }}
                    >
                        Ecoregion
                    </h5>
                    <div className="button-group flex-container">
                        <button className="button" type="button" onClick={handleClick("ECO3")}>
                            Level 3
                        </button>
                        <button className="button" type="button" onClick={handleClick("ECO4")}>
                            Level 4
                        </button>
                    </div>
                </div>
            </div>
        </React.Fragment>
    )
}

LayerChooser.propTypes = {
    setLayer: PropTypes.func.isRequired
}

export default connect(
    null,
    actions
)(LayerChooser)
