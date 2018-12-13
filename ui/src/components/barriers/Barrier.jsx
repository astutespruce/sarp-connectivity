// state: selected tab: details vs priorities.  TODO: put this in global state

import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import Details from "./Details"
import Priorities from "./Priorities"
import { BarrierPropType } from "../../CustomPropTypes"

import { setDetailsTab } from "../../actions/details"

const Barrier = ({ tab, barrier, onClose, setTab }) => {
    const { id, name, county, state } = barrier

    const handleDetailsClick = () => setTab("details")
    const handlePrioritiesClick = () => setTab("priorities")

    return (
        <React.Fragment>
            <div id="SidebarHeader" className="has-tabs">
                <div className="flex-container flex-justify-center flex-align-start">
                    <div className="flex-grow">
                        <h5 className="title is-5">{name || "Unknown name"}</h5>
                        <h5 className="subtitle is-6">
                            {county}, {state}
                        </h5>
                    </div>
                    <div className="icon button" onClick={onClose}>
                        <span className="fa fa-times-circle is-size-4" />
                    </div>
                </div>
                <div className="tabs">
                    <ul>
                        <li className={tab === "details" ? "is-active" : null}>
                            <a onClick={handleDetailsClick}>Overview</a>
                        </li>
                        <li className={tab === "priorities" ? "is-active" : null}>
                            <a onClick={handlePrioritiesClick}>Connectivity Ranks</a>
                        </li>
                    </ul>
                </div>
            </div>

            <div id="SidebarContent" className="flex-container-column">
                {tab === "details" ? <Details {...barrier} /> : <Priorities {...barrier} />}
            </div>

            <div className="text-align-center" style={{ padding: "1rem 0" }}>
                <a
                    href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for barrier: ${id}&body=I found the following problem with the SARP Inventory for this barrier:`}
                >
                    <i className="fas fa-envelope" />
                    &nbsp; Report a problem with this barrier
                </a>
            </div>
        </React.Fragment>
    )
}

Barrier.propTypes = {
    id: PropTypes.string.isRequired,
    tab: PropTypes.string.isRequired,
    barrier: BarrierPropType.isRequired,
    summaryUnit: PropTypes.string.isRequired,
    onClose: PropTypes.func.isRequired,
    setTab: PropTypes.func
}

Barrier.defaultProps = {
    setTab: tab => {
        console.log(`Set tab ${tab}`)
    }
}

const mapStateToProps = globalState => {
    const state = globalState.get("details")

    return {
        tab: state.get("tab")
    }
}

export default connect(
    mapStateToProps,
    { setTab: setDetailsTab }
)(Barrier)
