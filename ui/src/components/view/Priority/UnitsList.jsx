import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import { connect } from "react-redux"

import * as actions from "../../../actions/priority"

import { formatNumber } from "../../../utils/format"

import StartOverButton from "./StartOverButton"
import SubmitButton from "./SubmitButton"
import UnitListItem from "./UnitListItem"

const getPluralLabel = layer => {
    switch (layer) {
        case "State":
            return "states"
        case "County":
            return "counties"
        case "HUC6":
            return "basins"
        case "HUC8":
            return "subbasins"
        case "HUC12":
            return "subwatersheds"
        case "ECO3":
            return "ecoregions"
        case "ECO4":
            return "ecoregions"
        default:
            return "areas"
    }
}

const getSingularLabel = layer => {
    switch (layer) {
        case "State":
            return "state"
        case "County":
            return "county"
        case "HUC6":
            return "basin"
        case "HUC8":
            return "subbasin"
        case "HUC12":
            return "subwatershed"
        case "ECO3":
            return "ecoregion"
        case "ECO4":
            return "ecoregion"
        default:
            return "area"
    }
}

const getSingularArticle = layer => {
    if (layer === "ECO3" || layer === "ECO4") return "an"
    return "a"
}

const UnitsList = ({ type, layer, summaryUnits, selectUnit, setLayer, fetchQuery }) => {
    const pluralLabel = getPluralLabel(layer)
    const singularLabel = getSingularLabel(layer)
    const article = getSingularArticle(layer)

    let offNetworkCount = 0
    if (type === "dams" && summaryUnits.size > 0) {
        offNetworkCount = summaryUnits.toJS().reduce((out, v) => out + v.off_network_dams, 0)
    }

    return (
        <React.Fragment>
            <div id="SidebarHeader">
                <button className="link link-back" type="button" onClick={() => setLayer(null)}>
                    <span className="fa fa-reply" />
                    &nbsp; choose a different type of area
                </button>
                <h4 className="title is-4">Choose {pluralLabel}</h4>
            </div>
            <div id="SidebarContent">
                {summaryUnits.size === 0 ? (
                    <p className="is-size-6 text-help">
                        Select your {pluralLabel} of interest by clicking on them in the map.
                        <br />
                        <br />
                        If boundaries are not currently visible on the map, zoom in further until they appear.
                        <br />
                        <br />
                    </p>
                ) : (
                    <React.Fragment>
                        <b>Selected {pluralLabel}:</b>
                        <ul id="SummaryUnitList">
                            {summaryUnits.toJS().map(unit => (
                                <UnitListItem key={unit.id} unit={unit} type={type} onDelete={() => selectUnit(unit)} />
                            ))}
                        </ul>
                        <p className="is-size-6 has-text-grey" style={{ padding: "2rem 0" }}>
                            Select additional {pluralLabel} by clicking on them on the map. To unselect {article}{" "}
                            {singularLabel}, use the trash button above or click on it on the map.
                            {offNetworkCount > 0 ? (
                                <React.Fragment>
                                    <br />
                                    <br />
                                    Note: only {type} that have been snapped to the aquatic network are available for
                                    prioritization. There are {formatNumber(offNetworkCount, 0)} off-network {type} in
                                    your selected area.
                                </React.Fragment>
                            ) : null}
                        </p>
                    </React.Fragment>
                )}

                {layer !== "State" && layer !== "County" ? (
                    <p className="text-help">
                        <span className="icon">
                            <i className="fas fa-exclamation-triangle" />
                        </span>
                        Note: You can choose from {pluralLabel} outside the highlighted states in the Southeast, but the
                        barriers inventory is likely more complete only where {pluralLabel} overlap the highlighted
                        states.
                    </p>
                ) : null}
            </div>

            <div id="SidebarFooter">
                <div className="flex-container flex-justify-center flex-align-center">
                    <StartOverButton />

                    <SubmitButton
                        disabled={summaryUnits.size === 0}
                        onClick={() => fetchQuery(layer, summaryUnits.toJS())}
                        icon="search-location"
                        label={`Select ${type} in this area`}
                    />
                </div>
            </div>
        </React.Fragment>
    )
}

UnitsList.propTypes = {
    type: PropTypes.string.isRequired,
    layer: PropTypes.string.isRequired,
    summaryUnits: ImmutablePropTypes.set.isRequired,
    setLayer: PropTypes.func.isRequired,
    selectUnit: PropTypes.func.isRequired,
    fetchQuery: PropTypes.func.isRequired
}

const mapStateToProps = globalState => {
    const state = globalState.get("priority")

    return {
        type: state.get("type"),
        layer: state.get("layer"),
        summaryUnits: state.get("summaryUnits")
    }
}

export default connect(
    mapStateToProps,
    actions
)(UnitsList)
