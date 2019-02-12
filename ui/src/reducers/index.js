import { combineReducers } from "redux-immutable"
import { connectRouter } from "connected-react-router/immutable"

import { reducer as crossfilterReducer } from "./crossfilter"
import { reducer as summaryReducer } from "./summary"
import { reducer as priorityReducer } from "./priority"
import { reducer as detailsReducer } from "./details"
import { reducer as mapReducer } from "./map"

const rootReducer = history =>
    combineReducers({
        router: connectRouter(history),
        crossfilter: crossfilterReducer,
        priority: priorityReducer,
        summary: summaryReducer,
        details: detailsReducer,
        map: mapReducer
    })

export default rootReducer
