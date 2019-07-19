import React, { createContext, useContext } from 'react'
import PropTypes from 'prop-types'

const Context = createContext(null)

export const Provider = ({ children, barrierType }) => (
  <Context.Provider value={barrierType}>{children}</Context.Provider>
)

Provider.propTypes = {
  children: PropTypes.oneOfType([PropTypes.node, PropTypes.element]).isRequired,
  barrierType: PropTypes.string.isRequired, // "dams" or "barriers"
}

export const useBarrierType = () => {
  return useContext(Context)
}
