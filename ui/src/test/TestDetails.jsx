import React from "react"

import Barrier from "../components/barriers/Barrier"
import Sidebar from "../components/Sidebar"

const props = {
    tab: "details",
    summaryUnit: "state"
}

const barrier = {
    // Barrier props
    id: "s2",
    name: "Adams Lake and Dam", // may be blank
    county: "Houston County",
    state: "Alabama",
    lat: 31.145,
    lon: -83.413,
    river: "Adams River", // may be blank
    basin: "Alabama", // TODO: need a LUT of HUC6s to names
    height: 12,
    year: 1958,
    material: "unknown",
    purpose: "agriculture",
    condition: "not rated",

    numSpp: 3, // num T&E spps

    metrics: {
        length: 0.628,
        upstreamMiles: 0.628,
        downstreamMiles: 356.29,
        sizeclasses: 1,
        sinuosity: 1.1,
        landcover: 69.45
    },

    metricScores: {
        // TODO
    },

    priorities: {
        se: {
            nc: 0.427,
            wc: 0.257,
            ncwc: 0.342
        },
        state: {
            nc: 0.618,
            wc: 0.292,
            ncwc: 0.455
        },
        custom: {
            nc: 0.8,
            wc: 0.3,
            ncwc: 0.5
        }
    }
}

function TestDetails() {
    return (
        <Sidebar>
            <Barrier barrier={barrier} {...props} />
        </Sidebar>
    )
}

export default TestDetails
