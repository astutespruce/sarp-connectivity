import React from "react"
import PropTypes from "prop-types"
import ImmutablePropTypes from "react-immutable-proptypes"
import SummaryUnitListItem from "./SummaryUnitListItem"

const SummaryUnitChooser = ({ summaryUnits, onDeselectUnit, onBack, onSubmit }) => (
    <div id="SidebarContent">
        <a href="#" onClick={() => onBack()}>
            <span className="fa fa-reply" />
            &nbsp; choose a different summary level
        </a>
        <h4 className="subtitle is-4">Select area of interest</h4>

        {summaryUnits.size === 0 ? (
            <p className="is-size-6 has-text-grey">
                Select your area of interest by clicking on one or more summary units in the map. Click an area to
                select it.
                <br />
                <br />
                If units are not currently visible on the map, zoom in further until they appear.
                <br />
                <br />
            </p>
        ) : (
            <React.Fragment>
                <b>Selected areas:</b>
                <ul id="SummaryUnitList">
                    {summaryUnits.toJS().map(unit => (
                        <SummaryUnitListItem key={unit.id} unit={unit} onDelete={onDeselectUnit} />
                    ))}
                </ul>
                <p className="is-size-6 has-text-grey" style={{ padding: "2rem 0" }}>
                    Select additional areas by clicking on them on the map. To unselect an area, use the trash button
                    above or click on it on the map.
                </p>
                <div className="field is-grouped">
                    <button type="button" className="button is-white is-medium">
                        Cancel
                    </button>
                    <button type="button" className="button is-info is-medium" onClick={onSubmit}>
                        <i className="fa fa-search-location" />
                        Prioritize Barriers
                    </button>
                </div>
            </React.Fragment>
        )}
    </div>
)

SummaryUnitChooser.propTypes = {
    summaryUnits: ImmutablePropTypes.set.isRequired,
    onDeselectUnit: PropTypes.func.isRequired,
    onBack: PropTypes.func.isRequired,
    onSubmit: PropTypes.func.isRequired
}

export default SummaryUnitChooser
