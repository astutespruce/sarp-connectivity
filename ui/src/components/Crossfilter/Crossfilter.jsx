import { useReducer, useRef } from 'react'
import { Map, List, Set } from 'immutable'

import Crossfilter from 'crossfilter2'
import { isDebug } from 'util/dom'
import {
  aggregateByDimension,
  getRawTotal,
  getFilteredTotal,
  aggregateDimensionById,
} from './util'

// TODO: generalize handling of timestep
// can be a prop on the filter itself to calculate max, and then toss that in a stats object here
// dimensionStats: {
//   dim: {
//     'count':
//     'total':
//     'max'
//   }
// }

// returns true if passed in values contains the value
// values must be a Set
export const hasValue = filterValues => value => filterValues.has(value)

// Actions
export const RESET_FILTERS = 'RESET_FILTERS'
export const SET_FILTER = 'SET_FILTER' // payload is {field, filterValue}
export const SET_VALUE_FIELD = 'SET_VALUE_FIELD' // payload is {field}

// Incoming data is an immutableJS List of Maps
export const useCrossfilter = (data, filters, initValueField = null) => {
  const crossfilterRef = useRef(null)
  const dimensionsRef = useRef(null)

  // payload: {type: "SOME_TYPE", payload: <the_data>}
  const reducer = (state, { type, payload }) => {
    const { current: crossfilter } = crossfilterRef
    const { current: dimensions } = dimensionsRef

    if (isDebug) {
      console.log(`Handling ${type}`, payload)
      console.log('Prev state', state.toJS())
    }

    let newState = state

    switch (type) {
      case SET_FILTER: {
        const { field, filterValue } = payload
        const dimension = dimensions[field]
        const valueField = state.get('valueField')

        if (!dimension) {
          console.warn(
            `Filter requested on dimension that does not exist: ${field}`
          )
          return state
        }
        // console.log('dimension', dimension, field, filterValue)

        if (!filterValue || filterValue.size === 0) {
          // there are no filter values, so clear filter on this field
          dimension.filterAll()
        } else {
          const filterFunc = dimension.config.filterFunc(filterValue)
          dimension.filterFunction(filterFunc)
        }

        newState = state.merge({
          // convert Array from crossfilter back to an immutable List
          data: List(crossfilter.allFiltered()),
          filters: state.get('filters').set(field, filterValue),
          dimensionTotals: aggregateByDimension(dimensions, valueField),
          filteredTotal: getFilteredTotal(crossfilter, valueField),
          dimensionTotalsById: aggregateDimensionById(dimensions, valueField),
        })
        break
      }

      case RESET_FILTERS: {
        const { fields } = payload

        let newFilters = state.get('filters')
        const valueField = state.get('valueField')

        fields.forEach(field => {
          dimensions[field].filterAll()

          const filter = newFilters.get(field)
          newFilters = newFilters.set(field, filter ? filter.clear() : Set())
        })

        newState = state.merge({
          // convert Array from crossfilter back to an immutable List
          data: List(crossfilter.allFiltered()),
          filters: newFilters,
          dimensionTotals: aggregateByDimension(dimensions, valueField),
          filteredTotal: getFilteredTotal(crossfilter, valueField),
          dimensionTotalsById: aggregateDimensionById(dimensions, valueField),
        })
        break
      }

      case SET_VALUE_FIELD: {
        const { field } = payload

        newState = state.merge({
          valueField: field,
          dimensionTotals: aggregateByDimension(dimensions, field),
          filteredTotal: getFilteredTotal(crossfilter, field),
          total: getRawTotal(crossfilter, field),
          dimensionTotalsById: aggregateDimensionById(dimensions, field),
        })

        break
      }

      default: {
        console.error('unhandled action type', type)
        break
      }
    }

    if (isDebug) {
      console.log('Next state', newState.toJS())
    }

    return newState
  }

  // Initialize crossfilter and dimensions when useReducer is first setup
  const initialize = () => {
    // crossfilter depends on Array methods at the top level
    // so we shallowly convert the List to an Array.
    const crossfilter = Crossfilter(data.toArray())

    const dimensions = {}
    filters.forEach(filter => {
      const { field, isArray, getValue } = filter
      // default `getValue` function is identify function for field
      // const dimensionFunction = getValue || (d => d[field])
      const dimensionFunction =
        getValue ||
        (record => {
          const value = record.get(field)
          // if incoming value is an immutableJS object, convert it to JS first
          if (value && value.toJS !== undefined) {
            return value.toJS()
          }
          return value
        })
      const dimension = crossfilter.dimension(dimensionFunction, !!isArray)
      dimension.config = filter
      dimensions[field] = dimension
    })

    crossfilterRef.current = crossfilter
    dimensionsRef.current = dimensions

    if (isDebug) {
      window.crossfilter = crossfilter
      window.dimensions = dimensions
    }

    const total = getRawTotal(crossfilter, initValueField)

    // initial state
    return Map({
      // passed in data
      data,
      valueField: initValueField,

      // derived data
      total,
      filteredTotal: total,
      filters: Map(),
      dimensionTotals: aggregateByDimension(dimensions, initValueField),
      dimensionTotalsById: aggregateDimensionById(dimensions, initValueField),
    })
  }

  // returns {state, dispatch}
  return useReducer(reducer, undefined, initialize)
}
