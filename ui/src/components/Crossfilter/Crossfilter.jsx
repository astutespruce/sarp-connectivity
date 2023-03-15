/* eslint-disable no-underscore-dangle */

import { useState, useRef } from 'react'
import { op } from 'arquero'

window.op = op

import { reduceToObject, sum } from 'util/data'
import { isDebug } from 'util/dom'
import { columnsToObject, getDimensionCount, countByDimension } from './util'

// returns true if passed in values contains the value
// values must be a Set
export const hasValue = (filterValues) => (value) => filterValues.has(value)

const createDimensions = (filterConfig) => {
  const dimensions = {}
  filterConfig.forEach(({ filters }) => {
    filters.forEach((filter) => {
      const {
        field,
        // isArray, // TODO: handle isArray (can we update the field values to a set?)
        getValue,
      } = filter

      dimensions[field] = {
        ...filter,
        // default `getValue` function is identify function for field

        // FIXME: deprecated; only do this for isArray types
        // getValue: getValue || ((record) => record[field]),
      }
    })
  })

  if (isDebug) {
    window.dimensions = dimensions
  }

  return dimensions
}

export const Crossfilter = (filterConfig) => {
  // const dataRef = useRef(null)
  // const filteredDataRef = useRef(null)
  const dimensionsRef = useRef(createDimensions(filterConfig))

  // Memoize dimensions, so they only get created once

  // FIXME: remove
  console.log('filterConfig', filterConfig, dimensionsRef.current)

  // const getFilteredCount = () =>
  // filteredDataRef.current
  //   .rollup({ _count: (d) => op.sum(d._count) })
  //   .column('_count').data[0]

  const [state, setState] = useState(() => ({
    data: null,
    totalDimensionCounts: null,

    filteredData: null,
    filteredCount: 0,
    filters: {},
    hasFilters: false,
    dimensionCounts: null,
    filteredDimensionCounts: null,
    emptyDimensions: new Set(),
    emptyGroups: new Set(),
  }))

  const setData = (newData) => {
    if (isDebug) {
      console.log('setData', newData)
    }

    const { current: dimensions } = dimensionsRef

    // dataRef.current = newData
    // filteredDataRef.current = newData

    let dimensionCounts = null
    const emptyDimensions = new Set()
    const emptyGroups = new Set()

    if (newData !== null) {
      //   validate that expected fields are present
      const cols = new Set(newData.columnNames())
      Object.keys(dimensions).forEach((field) => {
        if (!cols.has(field)) {
          throw new Error(`Field is not present in data: ${field}`)
        }
      })

      dimensionCounts = countByDimension(newData, dimensions)

      filterConfig
        .filter(({ hasData }) => hasData && !hasData(newData))
        .forEach(({ id }) => {
          emptyGroups.add(id)
        })

      Object.entries(dimensionCounts).forEach(([field, counts]) => {
        if (!(counts && sum(Object.values(counts)) > 0)) {
          emptyDimensions.add(field)
        }
      })
    }

    setState(() => {
      const newState = {
        // only change on update of data:
        data: newData,
        totalDimensionCounts: dimensionCounts,

        // change on update to filters:
        filteredData: newData,
        filteredCount: newData
          .rollup({ _count: (d) => op.sum(d._count) })
          .column('_count').data[0],
        filters: {},
        hasFilters: false,
        dimensionCounts,

        emptyDimensions,
        emptyGroups,
      }

      if (isDebug) {
        console.log('Next state', newState)
      }

      return newState
    })
  }

  const setFilter = (filterField, filterValue) => {
    const { current: dimensions } = dimensionsRef

    if (!dimensions[filterField]) {
      console.warn(
        `Filter requested on dimension that does not exist: ${filterField}`
      )
    }

    setState((prevState) => {
      if (isDebug) {
        console.log('setFilter', filterField, filterValue)
        console.log('Prev state', prevState)
      }

      // FIXME: remove
      const start = Date.now()

      // const { current: data } = dataRef
      // const { current: dimensions } = dimensionsRef

      const {
        data,
        filters: { [filterField]: prevFilter, ...prevFilters },
      } = prevState

      // Create new instance, don't mutate
      const filters = { ...prevFilters }

      // only set if non-empty
      if (filterValue && filterValue.size) {
        filters[filterField] = filterValue
      }

      // reset filtered data
      // let filteredData = dataRef.current
      let filteredData = data

      const activeFilters = Object.entries(filters).filter(
        ([_, filter]) => filter && filter.size > 0
      )
      console.log('activeFilters', activeFilters)

      activeFilters.forEach(([field, filter]) => {
        // skip current field, that is filtered last
        if (field === filterField) {
          return
        }

        const { isArray } = dimensions[field]
        if (isArray) {
          // TODO: handle isArray filters
          console.log('TODO:', field, filter)
        } else {
          filteredData = filteredData
            .params({ field, values: [...filter] })
            .filter((d, $) => op.includes($.values, d[$.field]))

          console.log('applied filter', field, '=>', filteredData)
        }
      })

      window.filteredData = filteredData

      // calculate count of current field based on all other filters,
      // then apply filter to last field
      const currentDimensionCount = getDimensionCount(
        filteredData,
        dimensions[filterField]
      )

      if (filterValue && filterValue.size > 0) {
        // TODO: apply current filter last
        console.log('apply current filter', filterField, filterValue)
        const { isArray } = dimensions[filterField]
        if (isArray) {
          // TODO: handle isArray filters
          console.log('TODO:', filterField, filterValue)
        } else {
          filteredData = filteredData
            .params({ field: filterField, values: [...filterValue] })
            .filter((d, $) => op.includes($.values, d[$.field]))

          console.log('applied filter', filterField, '=>', filteredData)
        }
      }

      const dimensionCounts = countByDimension(filteredData, dimensions)
      dimensionCounts[filterField] = currentDimensionCount

      // filteredDataRef.current = filteredData

      const newState = {
        ...prevState,
        filteredData,
        filteredCount: filteredData
          .rollup({ _count: (d) => op.sum(d._count) })
          .column('_count').data[0],
        filters,
        hasFilters: activeFilters.length > 0,
        dimensionCounts,
      }

      if (isDebug) {
        console.log('Next state', newState)

        // FIXME: remove
        const end = Date.now()
        console.log(`Execution time: ${end - start} ms`)
      }

      return newState
    })
  }

  // TODO:
  const resetGroupFilters = (groupId) => {
    setState((prevState) => {
      if (isDebug) {
        console.log('resetGroupFilters')
        console.log('Prev state', prevState)
      }

      const { current: dimensions } = dimensionsRef
      const { filters: prevFilters } = prevState

      // Create new instance, don't mutate
      const newFilters = {
        ...prevFilters,
      }

      const groupFields = filterConfig
        .filter(({ id }) => id === groupId)[0]
        .filters.map(({ field }) => field)
      groupFields.forEach((field) => {
        const dimension = dimensions[field]
        dimension.filterAll()
        newFilters[field] = new Set()
      })

      const hasFilters =
        Object.values(newFilters).filter((filter) => filter && filter.size > 0)
          .length > 0

      const filteredData = prevState.data // FIXME:

      const newState = {
        ...prevState,
        filters: newFilters,
        hasFilters,
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

      const { current: dimensions } = dimensionsRef
      const { data } = prevState

      const newState = {
        ...prevState,
        filteredData: data,
        filteredCount: data
          .rollup({ _count: (d) => op.sum(d._count) })
          .column('_count').data[0],
        filters: {},
        hasFilters: false,
        dimensionCounts: countByDimension(data, dimensions),
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
    resetGroupFilters,
    resetFilters,
    state,

    // pass the original config back through so that we can
    // iterate over filters for display
    filterConfig,
  }
}
