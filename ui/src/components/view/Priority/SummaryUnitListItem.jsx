import React from "react"
import PropTypes from "prop-types"
import { formatNumber } from "../../../utils/format"

const SummaryUnitListItem = ({ unit, onDelete }) => {
    const { id } = unit
    const { name = id, dams = 0 } = unit
    return (
        <li className="flex-container flex-justify-space-between">
            <div style={{ maxWidth: 300 }}>
                {name}
                &nbsp;
                <span className="is-size-7 has-text-grey">({formatNumber(dams)} dams)</span>
            </div>
            <div>
                <span className="fa fa-trash cursor-pointer" onClick={() => onDelete(unit)} />
            </div>
        </li>
    )
}
SummaryUnitListItem.propTypes = {
    unit: PropTypes.object.isRequired,
    onDelete: PropTypes.func.isRequired
}

export default SummaryUnitListItem
