import { useState } from 'react'
import Crossfilter2 from 'crossfilter2'
import { isDebug } from 'util/dom'
import { useIsEqualMemo } from 'util/hooks'
import { countByDimension, getFilteredCount } from './util'

// returns true if passed in values contains the value
// values must be a Set
export const hasValue = (filterValues) => (value) => filterValues.has(value)

/**
 * Initialize crossfilter from the data and filters
 * @param {Array} data - records to index
 * @param {Array} filters - array of field configuration
 */
const initCrossfilter = (data, filterConfig) => {
  const crossfilter = Crossfilter2(data)

  const dimensions = {}
  filterConfig.forEach((filter) => {
    const { field, isArray, getValue } = filter
    // default `getValue` function is identify function for field
    const dimensionFunction = getValue || ((record) => record[field])

    const dimension = crossfilter.dimension(dimensionFunction, !!isArray)
    dimension.config = filter
    dimensions[field] = dimension
  })

  if (isDebug) {
    window.crossfilter = crossfilter
    window.dimensions = dimensions
  }
  return {
    crossfilter,
    dimensions,
  }
}

export const Crossfilter = (data, filterConfig) => {
  // Memoize construction of crossfilter and dimensions, so they only get created once
  const { crossfilter, dimensions } = useIsEqualMemo(
    () => initCrossfilter(data, filterConfig),
    [data]
  )

  // create the initial state in the callback so that we only construct it once
  const [state, setState] = useState(() => {
    const count = crossfilter.size()
    const initialState = {
      // passed in data
      data,

      // derived data
      count,
      filteredCount: count,
      filters: {},
      hasFilters: false,
      dimensionCounts: countByDimension(dimensions),
    }

    if (isDebug) {
      console.log('Initial state', initialState)
    }

    return initialState
  })

  const setData = (newData) => {
    if (isDebug) {
      console.log('setData')
    }

    setState(() => {
      // validate that expected fields are present
      if (newData.length > 0) {
        Object.keys(dimensions).forEach((field) => {
          if (newData[0][field] === undefined) {
            throw new Error(`Field is not present in data: ${field}`)
          }
        })
      }

      // remove all previous records
      crossfilter.remove(() => true)
      crossfilter.add(newData)
      const count = crossfilter.size()

      const dimensionCounts = countByDimension(dimensions)

      const newState = {
        data: newData,
        count,
        filteredCount: count,
        filters: {},
        hasFilters: false,
        dimensionCounts,
        emptyDimensions: Object.keys(dimensionCounts).filter(
          (id) => Object.keys(dimensionCounts[id]).length <= 1
        ),
      }

      if (isDebug) {
        console.log('Next state', newState)
      }

      return newState
    })
  }

  const setFilter = (field, filterValue) => {
    if (!dimensions[field]) {
      console.warn(
        `Filter requested on dimension that does not exist: ${field}`
      )
    }

    setState((prevState) => {
      if (isDebug) {
        console.log('setFilter', field, filterValue)
        console.log('Prev state', prevState)
      }

      const dimension = dimensions[field]
      if (!filterValue || filterValue.size === 0) {
        // there are no filter values, so clear filter on this field
        dimension.filterAll()
      } else {
        // default to hasValue if filterFunc is not provided in config
        const {
          config: { filterFunc = hasValue },
        } = dimension
        dimension.filterFunction(filterFunc(filterValue))
      }

      const { filters: prevFilters } = prevState

      // Create new instance, don't mutate
      const newFilters = {
        ...prevFilters,
        [field]: filterValue,
      }

      const hasFilters =
        Object.values(newFilters).filter((filter) => filter && filter.size > 0)
          .length > 0

      const newState = {
        ...prevState,
        data: crossfilter.allFiltered(),
        filters: newFilters,
        hasFilters,
        dimensionCounts: countByDimension(dimensions),
        filteredCount: getFilteredCount(crossfilter),
      }

      if (isDebug) {
        console.log('Next state', newState)
      }

      return newState
    })
  }

  const resetFilters = () => {
    setState((prevState) => {
      if (isDebug) {
        console.log('resetFilters')
        console.log('Prev state', prevState)
      }

      const { filters: prevFilters } = prevState

      // reset the filters on the dimenions
      Object.keys(prevFilters).forEach((field) => {
        dimensions[field].filterAll()
      })

      const newState = {
        ...prevState,
        data: crossfilter.allFiltered(),
        // remove all filter entries for these fields
        filters: {},
        hasFilters: false,
        dimensionCounts: countByDimension(dimensions),
        filteredCount: getFilteredCount(crossfilter),
      }

      if (isDebug) {
        console.log('Next state', newState)
      }

      return newState
    })
  }

  return {
    setData,
    setFilter,
    resetFilters,
    state,

    // pass the original config back through so that we can
    // iterate over filters for display
    filterConfig,
  }
}
