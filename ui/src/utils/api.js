/**
 * Converts units and filters into query parameters for API requests
 * @param {Array} units - array of objects with id property
 * @param {Map} filters - map of filter values, where filter name is key
 */
export const apiQueryParams = (units = [], filters = {}) => {
    const ids = units.map(({ id }) => id)
    const filterValues = Object.entries(filters).filter(([, v]) => v.length > 0)

    if (!(ids.length || filterValues.length)) return ""

    let query = `id=${ids.join(",")}`
    if (filterValues.length > 0) {
        query += `&${filterValues.map(([k, v]) => `${k}=${v.join(",")}`).join("&")}`
    }

    return query
}

export default { apiQueryParams }
