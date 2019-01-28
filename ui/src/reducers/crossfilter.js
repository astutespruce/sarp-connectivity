// import crossfilter from "crossfilter2"
import { Map, List, Set } from "immutable"

import { ON_LOAD, SET_FILTER, RESET, CLEAR } from "../actions/crossfilter"

// Get counts based on current filters
const countByDimension = dimensions => {
    let dimCounts = Map()

    dimensions.forEach(d => {
        const grouped = d.group().all()

        // Convert the array of key:count returned by crossfilter to a Map
        const counts = grouped.reduce((result, item) => {
            if (item) {
                return result.set(item.key, item.value)
            }
            return result
        }, Map())

        dimCounts = dimCounts.set(d.config.field, counts)
    })
    return dimCounts
}

const countFiltered = cf =>
    cf
        .groupAll()
        .reduceCount()
        .value()

const initialState = Map({
    isLoaded: false,
    crossfilter: null,
    dimensions: List(),
    dimensionIndex: Map(),
    filters: Map(),
    dimensionCounts: Map(),
    filteredCount: 0,
    total: 0
})

// TODO: when prioritization is changed, change the summaryUnit to custom
export const reducer = (state = initialState, { type, payload = {} }) => {
    switch (type) {
        case ON_LOAD: {
            const { crossfilter, dimensions } = payload

            const dimensionIndex = dimensions.reduce((out, dimension) => {
                out[dimension.config.field] = dimension
                return out
            }, {})

            const total = countFiltered(crossfilter)

            return state.merge({
                crossfilter: Map(crossfilter),
                dimensions: List(dimensions),
                dimensionIndex: Map(dimensionIndex),
                filters: dimensions.reduce((out, dimension) => out.set(dimension.config.field, Set()), Map()),
                dimensionCounts: countByDimension(dimensions),
                filteredCount: total,
                total
            })
        }
        case SET_FILTER: {
            const { filter, filterValues } = payload
            const dimension = state.get("dimensionIndex").get(filter)

            if (filterValues.size > 0) {
                dimension.filterFunction(d => filterValues.has(d))
            } else {
                dimension.filterAll()
            }

            return state.merge({
                dimensionCounts: countByDimension(state.get("dimensions")),
                filteredCount: countFiltered(state.get("crossfilter").toJS()),
                filters: state.get("filters").set(filter, filterValues)
            })
        }
        case RESET: {
            const dimensions = state.get("dimensions")

            // Note: this does not return new state but mutates it directly
            dimensions.forEach(d => {
                d.filterAll()
            })

            return state.merge({
                filters: dimensions.reduce((out, dimension) => out.set(dimension.config.field, Set()), Map()),
                dimensionCounts: countByDimension(dimensions),
                filteredCount: countFiltered(state.get("crossfilter").toJS())
            })
        }
        case CLEAR: {
            return initialState
        }
        default: {
            return state
        }
    }
}

export default reducer
