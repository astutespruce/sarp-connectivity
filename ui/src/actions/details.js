export const DETAILS_SET_TAB = "DETAILS_SET_TAB"
export const setDetailsTab = tab => ({
    type: DETAILS_SET_TAB,
    payload: { tab }
})

export const DETAILS_SET_UNIT = "DETAILS_SET_UNIT"
export const setDetailsUnit = unit => ({
    type: DETAILS_SET_UNIT,
    payload: {
        unit
    }
})
