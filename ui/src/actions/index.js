export const SET_SYSTEM = "SET_SYSTEM"
export const setSystem = system => ({
    type: SET_SYSTEM,
    payload: { system }
})

export const SET_LEVEL = 'SET_LEVEL'
export const setLevel = level => ({
    type: SET_LEVEL,
    payload: { level }
})

export const SET_UNIT = "SET_UNIT"
export const setUnit = (level, unit) => ({
    type: SET_UNIT,
    payload: { level, unit }
})

export const GO_BACK = "GO_BACK"
export const goBack = () => ({
    type: GO_BACK
})
