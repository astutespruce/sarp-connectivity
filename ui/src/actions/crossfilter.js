export const LOAD = "@@crossfilter/LOAD"
export const load = (data, filters) => ({
    type: LOAD,
    payload: {
        data,
        filters
    }
})

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
