import React from "react"
import PropTypes from "prop-types"

import { LAYER_NAMES, SYSTEMS, SYSTEM_UNITS, STATE_FIPS } from "../constants"
import data from "../data/unit_bounds.json"

// merge state name in
data.State.forEach(s => {
    s.name = STATE_FIPS[s.id]
    s.id = s.name
    s.layer = "State"
})

// expand county name to include " County"
data.County.forEach(c => {
    c.name += " County"
    c.layer = "County"
})

// for HUC and ECO units, add prefix for ID
SYSTEM_UNITS.HUC.forEach(layer => {
    data[layer].forEach(item => {
        item.layer = layer
    })
})
SYSTEM_UNITS.ECO.forEach(layer => {
    data[layer].forEach(item => {
        item.layer = layer
    })
})

const PREFIXES = {
    ECO3: "Level 3",
    ECO4: "Level 4"
}

const ListItem = ({ id, name, state, layer, showID, onClick }) => {
    const stateLabels = state
        ? state
            .split(",")
            .map(s => STATE_FIPS[s])
            .sort()
            .join(", ")
        : ""

    return (
        <li onClick={onClick}>
            <div className="has-text-weight-bold">
                {name}
                {showID && (
                    <span className="is-size-7 has-text-grey has-text-weight-normal no-wrap">
                        &nbsp;(
                        {layer && `${PREFIXES[layer] || layer}: `}
                        {id})
                    </span>
                )}
            </div>

            {stateLabels && <div className="has-text-grey-dark">{stateLabels}</div>}
        </li>
    )
}

ListItem.propTypes = {
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
    state: PropTypes.string,
    layer: PropTypes.string,
    showID: PropTypes.bool
}

ListItem.defaultProps = {
    state: "",
    layer: "",
    showID: false
}

const UnitSearch = ({ system, layer, value, onChange, onSelect }) => {
    const showID = layer ? !(layer === "State" || layer === "County") : system !== "ADM"

    const handleChange = ({ target: { value: inputValue } }) => {
        onChange(inputValue)
    }

    let results = []
    if (value && value !== "") {
        let units = []
        if (layer !== null) {
            units = data[layer]
        } else {
            units = SYSTEM_UNITS[system].reduce((collector, unit) => collector.concat(data[unit]), [])
        }

        // Filter out the top 10
        const expr = new RegExp(value, "gi")
        const filtered = units.filter(item => item.name.search(expr) !== -1 || (showID && item.id.search(expr) !== -1))
        results = filtered.slice(0, 10)
    }

    const searchLabel = layer ? LAYER_NAMES[layer] : SYSTEMS[system].toLowerCase()
    const suffix = ` name${
        (system && system !== "ADM") || (layer && !(layer === "State" || layer === "County")) ? " or ID" : ""
    }`

    return (
        <div id="UnitSearch">
            <h5 className="is-size-5">Search for {searchLabel}:</h5>
            <input
                className="input"
                type="text"
                placeholder={`${searchLabel}${suffix}`}
                value={value}
                onChange={handleChange}
            />
            {value !== "" && (
                <>
                    {results.length > 0 ? (
                        <ul>
                            {results.map(item => (
                                <ListItem key={item.id} {...item} showID={showID} onClick={() => onSelect(item)} />
                            ))}
                        </ul>
                    ) : (
                        <div className="has-text-grey text-align-center" style={{ margin: "1em 0" }}>
                            No results match your search
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

UnitSearch.propTypes = {
    value: PropTypes.string.isRequired,
    system: PropTypes.string,
    layer: PropTypes.string,

    onChange: PropTypes.func.isRequired,
    onSelect: PropTypes.func.isRequired
}

UnitSearch.defaultProps = {
    system: null,
    layer: null
}

export default UnitSearch
