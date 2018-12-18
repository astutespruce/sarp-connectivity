export const labelToGeoJSON = record => ({
    type: "Feature",
    geometry: {
        type: "Point",
        coordinates: record.point
    },
    properties: {
        label: record.label || ""
    }
})

export const labelsToGeoJSON = records => ({
    type: "FeatureCollection",
    features: records.map(labelToGeoJSON)
})

export const toGeoJSON = (record, x = "lon", y = "lat") => {
    const properties = {}
    Object.keys(record)
        .filter(f => f !== x && f !== y)
        .forEach(f => {
            properties[f] = record[f]
        })

    return {
        type: "Feature",
        geometry: {
            type: "Point",
            coordinates: [record[x], record[y]]
        },
        properties
    }
}

export const recordsToGeoJSON = records => records.map(toGeoJSON)

export default { labelToGeoJSON, labelsToGeoJSON }
