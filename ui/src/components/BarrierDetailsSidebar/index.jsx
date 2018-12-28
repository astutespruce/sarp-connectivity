// state: selected tab: details vs priorities.  TODO: put this in global state

import React from "react"
import PropTypes from "prop-types"
import { connect } from "react-redux"

import DamDetails from "./DamDetails"
import BarrierDetails from "./BarrierDetails"
import Scores from "./Scores"
import { BarrierPropType } from "../../CustomPropTypes"
import { isEmptyString } from "../../utils/string"
import { setDetailsTab } from "../../actions/details"

const BarrierDetailsSidebar = ({ type, mode, tab, barrier, onClose, setTab }) => {
    const { sarpid, name, hasnetwork, countyname, State } = barrier

    const details = type === "dams" ? <DamDetails {...barrier} /> : <BarrierDetails {...barrier} />

    const footer = (
        <div id="SidebarFooter">
            <div className="flex-container flex-justify-center flex-align-center">
                <a
                    href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
                        type === "dams" ? "dam" : "road-related barrier"
                    }: ${sarpid}&body=I found the following problem with the SARP Inventory for this barrier:`}
                >
                    <i className="fas fa-envelope" />
                    &nbsp; Report a problem with this barrier
                </a>
            </div>
        </div>
    )

    const defaultName = type === "dams" ? "Unknown name" : "Unnamed crossing"

    if (mode !== "results" || !barrier.ncwc_tier) {
        return (
            <React.Fragment>
                <div id="SidebarHeader" className="no-tabs">
                    <div className="flex-container flex-justify-center flex-align-start">
                        <div className="flex-grow">
                            <h5 className="title is-5">{!isEmptyString(name) ? name : defaultName}</h5>
                            {!isEmptyString(countyname) && !isEmptyString(State) ? (
                                <h5 className="subtitle is-6">
                                    {countyname}, {State}
                                </h5>
                            ) : null}
                        </div>
                        <div className="icon button" onClick={onClose}>
                            <span className="fa fa-times-circle is-size-4" />
                        </div>
                    </div>
                </div>

                <div id="SidebarContent" className="flex-container-column">
                    {details}
                </div>

                {footer}
            </React.Fragment>
        )
    }

    let scoreContent = null
    if (hasnetwork) {
        // Transform properties to priorities: <unit>_<metric>_score
        // For now, we are using tier to save space in data transport, so convert them to percent
        const scores = {}
        const units = ["se", "state"]
        const metrics = ["nc", "wc", "ncwc"]
        // TODO: "gainmiles", "landcover", "sinuosity", "sizeclasses",

        scores.custom = {}
        metrics.forEach(metric => {
            scores.custom[metric] = (100 * (19 - (barrier[`${metric}_tier`] - 1))) / 20
        })

        units.forEach(unit => {
            scores[unit] = {}
            metrics.forEach(metric => {
                scores[unit][metric] = (100 * (19 - (barrier[`${unit}_${metric}_tier`] - 1))) / 20
            })
        })

        scoreContent = <Scores scores={scores} />
    } else {
        scoreContent = <p className="has-text-grey">No connectivity information is available for this barrier.</p>
    }

    const handleDetailsClick = () => setTab("details")
    const handlePrioritiesClick = () => setTab("priorities")

    return (
        <React.Fragment>
            <div id="SidebarHeader" className="has-tabs">
                <div className="flex-container flex-justify-center flex-align-start">
                    <div className="flex-grow">
                        <h5 className="title is-5">{!isEmptyString(name) ? name : defaultName}</h5>
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
                {tab === "details" ? details : scoreContent}
            </div>

            {footer}
        </React.Fragment>
    )
}

BarrierDetailsSidebar.propTypes = {
    type: PropTypes.string.isRequired,
    mode: PropTypes.string.isRequired,
    tab: PropTypes.string.isRequired,
    barrier: BarrierPropType.isRequired,
    onClose: PropTypes.func.isRequired,
    setTab: PropTypes.func.isRequired
}

const mapStateToProps = globalState => {
    const state = globalState.get("details")

    return {
        mode: globalState.get("priority").get("mode"),
        tab: state.get("tab"),
        type: globalState.get("priority").get("type")
    }
}

export default connect(
    mapStateToProps,
    { setTab: setDetailsTab }
)(BarrierDetailsSidebar)
