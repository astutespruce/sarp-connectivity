import React, { createContext, useState, useContext } from 'react'
import PropTypes from 'prop-types'

import { Crossfilter } from './Crossfilter'

/**
 * Provide Crossfilter as a context so that components deeper in the
 * component tree can access crossfilter state or dispatch.
 */
const Context = createContext()

export const Provider = ({ filterConfig, children }) => {
  // init crossfilter with empty data
  const crossfilter = Crossfilter([], filterConfig)
  return <Context.Provider value={crossfilter}>{children}</Context.Provider>
}

Provider.propTypes = {
  filterConfig: PropTypes.array.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.element,
    PropTypes.array,
  ]).isRequired,
}

/**
 * Return crossfilter {state, setFilter, resetFilters, filterConfig} values
 */
export const useCrossfilter = () => {
  return useContext(Context)
}
