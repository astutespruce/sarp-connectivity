// state: selected tab: details vs priorities.  TODO: put this in global state

import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import Details from "./Details"
import Scores from "./Scores"
import { BarrierPropType } from "../../CustomPropTypes"

import { setDetailsTab } from "../../actions/details"

const Barrier = ({ type, tab, barrier, onClose, setTab }) => {
    const { sarpid, name, hasnetwork, countyname, State } = barrier

    let scoreContent = null
    if (hasnetwork) {
        // Transform properties to priorities: <unit>_<metric>_score
        const scores = {}
        const units = ["se", "state"] // TODO: custom
        const metrics = ["gainmiles", "landcover", "sinuosity", "sizeclasses", "nc", "wc", "ncwc"]

        units.forEach(unit => {
            scores[unit] = {}
            metrics.forEach(metric => {
                scores[unit][metric] = barrier[`${unit}_${metric}_score`]
            })
        })

        scoreContent = <Scores scores={scores} />
    } else {
        scoreContent = <p className="text-help">No connectivity information is available for this barrier.</p>
    }

    const handleDetailsClick = () => setTab("details")
    const handlePrioritiesClick = () => setTab("priorities")

    return (
        <React.Fragment>
            <div id="SidebarHeader" className="has-tabs">
                <div className="flex-container flex-justify-center flex-align-start">
                    <div className="flex-grow">
                        <h5 className="title is-5">{name && name !== "null" ? name : "Unknown name"}</h5>
                        <h5 className="subtitle is-6">
                            {countyname}, {State}
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
                {tab === "details" ? <Details type={type} {...barrier} /> : scoreContent}
            </div>

            <div id="SidebarFooter">
                <div className="flex-container flex-justify-center flex-align-center">
                    <a
                        href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for barrier: ${sarpid}&body=I found the following problem with the SARP Inventory for this barrier:`}
                    >
                        <i className="fas fa-envelope" />
                        &nbsp; Report a problem with this barrier
                    </a>
                </div>
            </div>
        </React.Fragment>
    )
}

Barrier.propTypes = {
    type: PropTypes.string.isRequired,
    tab: PropTypes.string.isRequired,
    barrier: BarrierPropType.isRequired,
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
        tab: state.get("tab"),
        type: globalState.get("priority").get("type")
    }
}

export default connect(
    mapStateToProps,
    { setTab: setDetailsTab }
)(Barrier)
