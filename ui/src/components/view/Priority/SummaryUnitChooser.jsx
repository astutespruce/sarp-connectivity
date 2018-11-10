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
        <h5 className="is-size-5">Select area of interest</h5>
        <p className="is-size-7 has-text-grey">
            Select your area of interest by clicking on one or more summary units in the map. Click an area to select it
            and click it again to deselect it.
            <br />
            <br />
            If units are not currently visible on the map, zoom in further until they appear.
            <br />
            <br />
        </p>

        {summaryUnits.size > 0 && (
            <React.Fragment>
                <b>Selected areas:</b>
                <ul id="SummaryUnitList">
                    {summaryUnits.toJS().map(unit => (
                        <SummaryUnitListItem key={unit.id} unit={unit} onDelete={onDeselectUnit} />
                    ))}
                </ul>
                <div>
                    <button type="button" className="button" onClick={onSubmit}>
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
