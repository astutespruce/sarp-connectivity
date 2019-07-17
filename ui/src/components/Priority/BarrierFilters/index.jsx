import React from 'react'
import PropTypes from 'prop-types'

import { useBarrierInfo, useBarrierType } from 'components/Data'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'

import { LoadingSpinner, ErrorMessage } from 'components/Sidebar'

import Filters from './Filters'

import { FILTERS } from '../../../../config/filters'

const BarrierFilters = ({ layer, summaryUnits, onBack, onFilterChange, onSubmit }) => {
  const { csv, error } = useBarrierInfo({
    layer,
    summaryUnits,
  })

  const barrierType = useBarrierType()
  const filterConfig = FILTERS[barrierType]

  if (csv) {
    return (
      <CrossfilterProvider data={csv} filterConfig={filterConfig}>
        <Filters onBack={onBack} onFilterChange={onFilterChange} onSubmit={onSubmit} />
      </CrossfilterProvider>
    )
  }

  if (error) {
    return <ErrorMessage>{error}</ErrorMessage>
  }

  // still loading
  return <LoadingSpinner />
}

BarrierFilters.propTypes = {
  layer: PropTypes.string.isRequired,
  summaryUnits: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ).isRequired,
  onBack: PropTypes.func.isRequired,
  onFilterChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default BarrierFilters
