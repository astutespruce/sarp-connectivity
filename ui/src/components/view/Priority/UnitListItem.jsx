/* eslint-disable camelcase */
import React from "react"
import PropTypes from "prop-types"

import { formatNumber } from "../../../utils/format"
import { STATE_FIPS } from "../../../constants"

const SummaryUnitListItem = ({ type, layer, unit, onDelete }) => {
    const { id } = unit
    const { name = id, dams = 0, barriers = 0, off_network_dams = 0, off_network_barriers = 0 } = unit

    const count = type === "dams" ? dams - off_network_dams : barriers - off_network_barriers

    return (
        <li className="flex-container flex-justify-space-between">
            <div style={{ maxWidth: 320 }}>
                <div className="is-size-5">
                    {name}
                    {layer === "County" ? `, ${STATE_FIPS[id.slice(0, 2)]}` : null}
                </div>
                {layer === "HUC6" || layer === "HUC8" || layer === "HUC12" ? <div>HUC: {id}</div> : null}

                <div className="has-text-grey">
                    ({formatNumber(count)} {type})
                </div>
            </div>
            <div>
                <span className="delete" onClick={() => onDelete(unit)} />
            </div>
        </li>
    )
}
SummaryUnitListItem.propTypes = {
    type: PropTypes.string.isRequired,
    layer: PropTypes.string.isRequired,
    unit: PropTypes.object.isRequired,
    onDelete: PropTypes.func.isRequired
}

export default SummaryUnitListItem
