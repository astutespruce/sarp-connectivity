import crossfilter from "crossfilter2"

export const LOAD = "@@crossfilter/LOAD"
export const load = (data, filters) => {
    const cf = crossfilter(data)

    const dimensions = filters.map(filter => {
        const { field, dimensionIsArray = false } = filter

        // default is identify function for field
        const dimensionFunction = filter.dimensionFunction || (d => d[field])
        const dimension = cf.dimension(dimensionFunction, !!dimensionIsArray)
        dimension.config = filter
        return dimension
    })

    return {
        type: LOAD,
        payload: {
            crossfilter: cf,
            dimensions
        }
    }
}

export const SET_FILTER = "@@crossfilter/SET_FILTER"
export const setFilter = (filter, filterValues) => ({
    type: SET_FILTER,
    payload: {
        filter,
        filterValues
    }
})

export const RESET = "@@crossfilter/RESET"
export const reset = () => ({
    type: RESET
})

export const CLEAR = "@@crossfilter/CLEAR"
export const clear = () => ({
    type: CLEAR
})
