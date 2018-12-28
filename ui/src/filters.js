import {
    HEIGHT,
    CONSTRUCTION,
    PURPOSE,
    FEASIBILITY,
    RARESPP,
    STREAMORDER,
    GAINMILES,
    BARRIER_SEVERITY,
    CROSSING_TYPE,
    ROAD_TYPE,
    DAM_CONDITION,
    BARRIER_CONDITION
} from "./constants"

const getIntKeys = obj =>
    Object.keys(obj)
        .map(k => parseInt(k, 10))
        .sort()

// Each filter needs to have a dimension above that matches the key here
export const DAM_FILTERS = [
    {
        field: "feasibility",
        title: "Feasibility",
        keys: getIntKeys(FEASIBILITY),
        labelFunction: d => FEASIBILITY[d],
        help:
            "Note: feasibility is based on further reconnaissance to evaluate individual barriers. Values are provided only for those that have been evaluated. There may be more feasible or infeasible dams than are indicated above."
    },
    {
        field: "gainmilesclass",
        title: "Miles Gained",
        keys: getIntKeys(GAINMILES),
        labelFunction: d => GAINMILES[d]
    },
    {
        field: "heightclass",
        title: "Dam Height",
        keys: getIntKeys(HEIGHT),
        labelFunction: d => HEIGHT[d],
        help:
            "Note: height information is only available for a small number of dams.  Not all data sources recorded this information."
    },
    {
        field: "sizeclasses",
        title: "Upstream Size Classes",
        keys: [0, 1, 2, 3, 4, 5, 6, 7],
        labelFunction: d => d
    },
    {
        field: "raresppclass",
        title: "Number of Rare Species",
        keys: getIntKeys(RARESPP),
        labelFunction: d => RARESPP[d],
        help:
            "Note: Rare species information is based on occurrences of one or more federally threatened or endangered aquatic species within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time."
    },
    {
        field: "streamorderclass",
        title: "Stream Order (NHD modified Strahler)",
        keys: getIntKeys(STREAMORDER),
        labelFunction: d => STREAMORDER[d]
    },
    {
        field: "condition",
        title: "Dam Condition",
        keys: getIntKeys(DAM_CONDITION),
        labelFunction: d => DAM_CONDITION[d],
        help:
            "Note: condition information is only available for a small number of dams.  Not all data sources recorded this information."
    },
    {
        field: "construction",
        title: "Dam Construction Materials",
        keys: getIntKeys(CONSTRUCTION),
        labelFunction: d => CONSTRUCTION[d],
        help:
            "Note: construction information is only available for a small number of dams.  Not all data sources recorded this information."
    },
    {
        field: "purpose",
        title: "Purpose",
        keys: getIntKeys(PURPOSE),
        labelFunction: d => PURPOSE[d],
        help:
            "Note: purpose information is only available for a small number of dams.  Not all data sources recorded this information."
    }
]

export const BARRIER_FILTERS = [
    {
        field: "severityclass",
        title: "Barrier Severity",
        keys: getIntKeys(BARRIER_SEVERITY),
        labelFunction: d => BARRIER_SEVERITY[d]
    },
    {
        field: "crossingtypeclass",
        title: "Crossing Type",
        keys: getIntKeys(CROSSING_TYPE),
        labelFunction: d => CROSSING_TYPE[d]
    },
    {
        field: "roadtypeclass",
        title: "Road Type",
        keys: getIntKeys(ROAD_TYPE),
        labelFunction: d => ROAD_TYPE[d]
    },
    {
        field: "gainmilesclass",
        title: "Miles Gained",
        keys: getIntKeys(GAINMILES),
        labelFunction: d => GAINMILES[d]
    },
    {
        field: "conditionclass",
        title: "Barrier Condition",
        keys: getIntKeys(BARRIER_CONDITION),
        labelFunction: d => BARRIER_CONDITION[d]
    },
    {
        field: "sizeclasses",
        title: "Upstream Size Classes",
        keys: [0, 1, 2, 3, 4, 5, 6, 7],
        labelFunction: d => d
    },
    {
        field: "raresppclass",
        title: "Number of Rare Species",
        keys: getIntKeys(RARESPP),
        labelFunction: d => RARESPP[d],
        help:
            "Note: Rare species information is based on occurrences of one or more federally threatened or endangered aquatic species within the same subwatershed as the dam.  These species may or may not be impacted by this dam.  Information on rare species is very limited and comprehensive information has not been provided for all states at this time."
    }
]
