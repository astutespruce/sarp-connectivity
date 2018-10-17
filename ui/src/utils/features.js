/**
 * Get the parent ID based on the well-known ID coding scheme of the system:
 * HUC: trim last 2 characters off
 * ecoregion: trim off everyting after last period
 *
 * @param {String} system
 * @param {String} id
 * Returns {String} - parentId
 */
export const getParentId = (system, id) => {
    switch (system) {
        case "HUC": {
            return id.substring(0, id.length - 2)
        }
        case "ecoregion": {
            return id.substring(0, id.lastIndexOf("."))
        }
    }
    return null // not a known system
}

export default { getParentId }
