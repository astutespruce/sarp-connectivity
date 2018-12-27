/* eslint-disable camelcase */
import React from "react"
import PropTypes from "prop-types"
import { formatNumber } from "../../../utils/format"

const SummaryUnitListItem = ({ type, unit, onDelete }) => {
    const { id } = unit
    const { name = id, dams = 0, barriers = 0, off_network_dams = 0, off_network_barriers = 0 } = unit

    const count = type === "dams" ? dams - off_network_dams : barriers - off_network_barriers

    return (
        <li className="flex-container flex-justify-space-between">
            <div style={{ maxWidth: 300 }}>
                {name}
                &nbsp;
                <span className="is-size-7 has-text-grey">
                    ({formatNumber(count)} {type})
                </span>
            </div>
            <div>
                <span className="fa fa-trash cursor-pointer" onClick={() => onDelete(unit)} />
            </div>
        </li>
    )
}
SummaryUnitListItem.propTypes = {
    type: PropTypes.string.isRequired,
    unit: PropTypes.object.isRequired,
    onDelete: PropTypes.func.isRequired
}

export default SummaryUnitListItem
