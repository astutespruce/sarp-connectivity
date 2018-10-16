export const SET_SYSTEM = "SET_SYSTEM"
export const setSystem = system => ({
    type: SET_SYSTEM,
    payload: { system }
})

export const SET_UNIT = "SET_UNIT"
export const setUnit = unit => ({
    type: SET_UNIT,
    payload: { unit }
})
