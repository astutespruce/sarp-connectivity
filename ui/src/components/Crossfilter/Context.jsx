import React, { createContext, useContext } from 'react'
import PropTypes from 'prop-types'

import { Crossfilter } from './Crossfilter'

/**
 * Provide Crossfilter as a context so that components deeper in the
 * component tree can access crossfilter state or dispatch.
 */
export const Context = createContext()

export const Provider = ({ data, filterConfig, children }) => {
  const value =
    data && data.length > 0 ? Crossfilter(data, filterConfig) : { state: {} }

  return <Context.Provider value={value}>{children}</Context.Provider>
}

Provider.propTypes = {
  data: PropTypes.array.isRequired,
  filterConfig: PropTypes.array.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.element,
    PropTypes.array,
  ]).isRequired,
}

// Hook for easier use in context
export const useCrossfilter = () => {
  return useContext(Context)
}
