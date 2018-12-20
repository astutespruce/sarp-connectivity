import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import SummaryUnitListItem from "./SummaryUnitListItem"

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

const SummaryUnitChooser = ({ layer, summaryUnits, onDeselectUnit, onBack }) => {
    const pluralLabel = getPluralLabel(layer)
    const singularLabel = getSingularLabel(layer)
    const article = getSingularArticle(layer)

    return (
        <React.Fragment>
            <div id="SidebarHeader">
                <button className="link link-back" type="button" onClick={() => onBack()}>
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
                                <SummaryUnitListItem key={unit.id} unit={unit} onDelete={onDeselectUnit} />
                            ))}
                        </ul>
                        <p className="is-size-6 has-text-grey" style={{ padding: "2rem 0" }}>
                            Select additional {pluralLabel} by clicking on them on the map. To unselect {article}{" "}
                            {singularLabel}, use the trash button above or click on it on the map.
                        </p>
                    </React.Fragment>
                )}
            </div>
        </React.Fragment>
    )
}

SummaryUnitChooser.propTypes = {
    layer: PropTypes.string.isRequired,
    summaryUnits: ImmutablePropTypes.set.isRequired,
    onDeselectUnit: PropTypes.func.isRequired,
    onBack: PropTypes.func.isRequired
}

export default SummaryUnitChooser
