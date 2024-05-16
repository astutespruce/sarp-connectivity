import { useState, useRef } from 'react'
import { op, agg, escape } from 'arquero'

import { sum, reduceToObject } from 'util/data'
import { isDebug } from 'util/dom'
import { applyFilters, createDimensions, countByDimension } from './util'

export const Crossfilter = (filterConfig) => {
  const dimensionsRef = useRef(createDimensions(filterConfig))

  if (isDebug) {
    window.dimensions = dimensionsRef.current
  }

  const [state, setState] = useState(() => ({
    data: null,
    totalDimensionCounts: null,

    filteredData: null,
    filteredCount: 0,
    filters: {},
    hasFilters: false,
    dimensionCounts: null,
    emptyDimensions: new Set(),
    emptyGroups: new Set(),
  }))

  const setData = (rawData) => {
    let newData = rawData

    if (isDebug) {
      console.log('setData', newData)
    }

    const { current: dimensions } = dimensionsRef

    let dimensionCounts = null
    const emptyDimensions = new Set()
    const emptyGroups = new Set()

    if (newData !== null) {
      // validate that expected fields are present and split array fields
      const cols = new Set(newData.columnNames())
      Object.values(dimensions).forEach(({ field, isArray }) => {
        if (!cols.has(field)) {
          throw new Error(`Field is not present in data: ${field}`)
        }
        if (isArray) {
          newData = newData
            // .params({ field })
            .derive({
              // [field]: (d, $) => op.split(d[$.field], ','),
              // temporary shim: build does not work with unescaped expressions
              [field]: escape((d) => op.split(d[field], ',')),
            })
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
        filteredCount:
          newData !== null ? agg(newData, (d) => op.sum(d._count)) : 0,
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

      const start = Date.now()

      const {
        data,
        totalDimensionCounts,
        // discard prev filter
        filters: { [filterField]: prevFilter, ...prevFilters },
      } = prevState

      // Create new instance, don't mutate
      const filters = { ...prevFilters }

      // only set if non-empty
      if (filterValue && filterValue.size) {
        filters[filterField] = filterValue
      }

      // reset filtered data to full data
      let filteredData = data
      let dimensionCounts = totalDimensionCounts

      const hasFilters =
        Object.entries(filters).filter(
          /* eslint-disable-next-line no-unused-vars */
          ([_, filter]) => filter && filter.size > 0
        ).length > 0

      if (hasFilters) {
        const {
          data: actuallyFilteredData,
          dimensionCounts: filteredDimensionCounts,
        } = applyFilters(data, dimensions, filters)
        filteredData = actuallyFilteredData
        dimensionCounts = filteredDimensionCounts
      }

      const newState = {
        ...prevState,
        filteredData,
        filteredCount:
          filteredData.numRows() > 0
            ? agg(filteredData, (d) => op.sum(d._count))
            : 0,
        filters,
        hasFilters,
        dimensionCounts,
      }

      if (isDebug) {
        console.log('Next state', newState)

        const end = Date.now()
        console.log(`Execution time: ${end - start} ms`)
      }

      return newState
    })
  }

  const resetGroupFilters = (groupId) => {
    setState((prevState) => {
      if (isDebug) {
        console.log('resetGroupFilters')
        console.log('Prev state', prevState)
      }

      const { current: dimensions } = dimensionsRef
      const { data, totalDimensionCounts, filters: prevFilters } = prevState

      // Create new instance, don't mutate
      const filters = {}

      const groupFields = filterConfig
        .filter(({ id }) => id === groupId)[0]
        .filters.reduce(...reduceToObject('field', () => true))

      Object.entries(prevFilters)
        .filter(
          ([field, filter]) => !groupFields[field] && filter && filter.size > 0
        )
        .forEach(([field, filter]) => {
          filters[field] = filter
        })

      // reset filtered data to full data
      let filteredData = data
      let dimensionCounts = totalDimensionCounts

      const hasFilters = Object.keys(filters).length > 0

      if (hasFilters) {
        const {
          data: actuallyFilteredData,
          dimensionCounts: filteredDimensionCounts,
        } = applyFilters(data, dimensions, filters)
        filteredData = actuallyFilteredData
        dimensionCounts = filteredDimensionCounts
      }

      const newState = {
        ...prevState,
        filteredData,
        filteredCount:
          filteredData.numRows() > 0
            ? agg(filteredData, (d) => op.sum(d._count))
            : 0,
        filters,
        hasFilters,
        dimensionCounts,
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

      const { data, totalDimensionCounts } = prevState

      const newState = {
        ...prevState,
        filteredData: data,
        filteredCount: agg(data, (d) => op.sum(d._count)),
        filters: {},
        hasFilters: false,
        dimensionCounts: totalDimensionCounts,
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
