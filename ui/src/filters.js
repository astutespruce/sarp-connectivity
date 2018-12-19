import { Map } from "immutable"
import crossfilter from "crossfilter2"
// import { objArrayToObj } from "./utils"
// import {
//     stateNames,
//     sizeClassLabels,
//     spps,
//     nfhpLabels,
//     estuaryTypes,
//     sizeClasses,
//     nfhpCodes,
//     bioticTypes,
//     bioticInfo,
//     sppCountClasses,
//     sppCountClassLabels
// } from "./constants"
// import { splitWords } from "./utils"

import { HEIGHT, FEASIBILITY, RARESPP, STREAMORDER, GAINMILES } from "./constants"

// Returns true if d exists in filterValues
// Only applies where a record has a singular value of d
// or dimension is set with isArray=true
export const existsFilter = (filterValues, d) =>
    // return filterValues.indexOf(d) !== -1
    filterValues.has(d)

const getIntKeys = obj =>
    Object.keys(obj)
        .map(k => parseInt(k, 10))
        .sort()

// Each filter needs to have a dimension above that matches the key here
export const filterConfig = {
    feasibility: {
        title: "Feasibility",
        keys: getIntKeys(FEASIBILITY),
        labelFunction: d => FEASIBILITY[d]
    },
    height: {
        title: "Dam Height",
        keys: getIntKeys(HEIGHT),
        labelFunction: d => HEIGHT[d]
    },
    sizeclasses: {
        title: "Upstream Size Classes",
        keys: [0, 1, 2, 3, 4, 5, 6, 7],
        labelFunction: d => d
    },
    rarespp: {
        title: "Number of Rare Species",
        keys: getIntKeys(RARESPP),
        labelFunction: d => RARESPP[d]
    },
    streamorder: {
        title: "Stream Order (NHD modified Strahler)",
        keys: getIntKeys(STREAMORDER),
        labelFunction: d => STREAMORDER[d]
    },
    gainmiles: {
        title: "Miles Gained",
        keys: getIntKeys(GAINMILES),
        labelFunction: d => GAINMILES[d]
    }
}

export const allFilters = ["feasibility", "height", "sizeclasses", "rarespp", "streamorder", "gainmiles"]

export function initCrossfilter(data) {
    // Create global crossfilter and dimensions
    const cf = crossfilter(data)
    const dims = {}

    Object.keys(filterConfig).forEach(f => {
        const config = filterConfig[f]
        const dimensionFunction = config.dimensionFunction || (d => d[f]) // default is identify function for field
        dims[f] = cf.dimension(dimensionFunction, !!config.dimensionIsArray)
    })

    // we use these as globals in various places, need them on window for easy access
    window.cf = cf
    window.dims = dims
}

// Get counts based on current filters
export const getDimensionCounts = () => {
    let dimCounts = Map()
    allFilters.forEach(d => {
        const grouped = window.dims[d].group().all()

        // Convert the array of key:count returned by crossfilter to a Map
        const counts = grouped.reduce((result, item) => {
            if (item) {
                return result.set(item.key, item.value)
            }
            return result
        }, Map())

        dimCounts = dimCounts.set(d, counts)
    })
    return dimCounts
}

window.getDimensionCounts = getDimensionCounts
