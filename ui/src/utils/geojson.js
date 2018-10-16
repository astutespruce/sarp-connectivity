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

export default { labelToGeoJSON, labelsToGeoJSON }
