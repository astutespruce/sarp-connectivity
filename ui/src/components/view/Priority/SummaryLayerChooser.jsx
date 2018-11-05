import React from "react"
import PropTypes from "prop-types"

import { LAYER_CONFIG } from "../../map/config"

const SummaryLayerChooser = ({ onSelect, onBack }) => {
    const handleClick = id => () => onSelect(id)

    return (
        <div id="SidebarContent">
            <a href="#" onClick={() => onBack()}>
                <span className="fa fa-reply" />
                &nbsp; back to Southeast region
            </a>
            <h5 className="is-size-5">View priorities at another level</h5>
            <div id="SummaryUnitChooser">
                <h6
                    style={{
                        marginTop: "1em"
                    }}
                >
                    Administrative unit
                </h6>
                <div>
                    <a href="#" onClick={handleClick("State")}>
                        State
                    </a>
                </div>
                <h6
                    style={{
                        marginTop: "1em"
                    }}
                >
                    Hydrologic unit
                </h6>
                {LAYER_CONFIG.filter(({ group }) => group === "HUC").map(({ id, title }) => (
                    <a href="#" key={id} onClick={handleClick(id)}>
                        {title}
                    </a>
                ))}

                <h6
                    style={{
                        marginTop: "1em"
                    }}
                >
                    Ecoregion
                </h6>
                {LAYER_CONFIG.filter(({ group }) => group === "ECO").map(({ id, title }) => (
                    <a href="#" key={id} onClick={handleClick(id)}>
                        {title}
                    </a>
                ))}
            </div>
        </div>
    )
}

SummaryLayerChooser.propTypes = {
    onSelect: PropTypes.func.isRequired,
    onBack: PropTypes.func.isRequired
}

export default SummaryLayerChooser
