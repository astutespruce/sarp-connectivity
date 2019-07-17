import React from 'react'
import PropTypes from 'prop-types'
import { FaTimesCircle } from 'react-icons/fa'

import { useBarrierType } from 'components/Data'
import { Filter } from 'components/Filters'
import { useCrossfilter } from 'components/Crossfilter'
import { ExpandableParagraph } from 'components/Text'
import { Flex } from 'components/Grid'

import styled, { themeGet } from 'style'
import {formatNumber} from 'util/format'

import BackLink from '../BackLink'
import SubmitButton from '../SubmitButton'
import StartOverButton from '../StartOverButton'
import { Wrapper, Header, Footer, Title as BaseTitle, Content } from '../styles'


const Title = styled(BaseTitle)`margin-bottom: 0;`


const CountContainer = styled(Flex).attrs({
  alignItems: 'center',
  justifyContent: 'space-between',
})``

const Count = styled.div`
  color: ${themeGet('colors.grey.700')};
`

const ResetLink = styled(Flex).attrs({ alignItems: 'center' })`
  color: ${themeGet('colors.highlight.500')};
  cursor: pointer;
`

const ResetIcon = styled(FaTimesCircle)`
  height: 1em;
  width: 1em;
  margin-right: 0.5em;
  color: ${themeGet('colors.highlight.500')};
`

const HelpText = styled(ExpandableParagraph)`
color: ${themeGet('colors.grey.700')};
`


const Filters = ({ onBack, onSubmit }) => {
  const barrierType = useBarrierType()
  const { state, filterConfig, resetFilters } = useCrossfilter()
  const { filteredCount, hasFilters } = state

  const handleReset = () => {
    resetFilters()
  }

  return (
    <Wrapper>
      <Header>
        <BackLink label="modify area of interest" onClick={onBack} />
        <Title>Filter {barrierType}</Title>

        <CountContainer>
          <Count>{formatNumber(filteredCount, 0)} selected</Count>
          {hasFilters && (
            <ResetLink onClick={handleReset}>
              <ResetIcon />
              <div>reset filters</div>
            </ResetLink>
          )}
        </CountContainer>
      </Header>

      <Content>
      <HelpText snippet={`[OPTIONAL] Use the filters below to select the ${barrierType} that meet
        your needs. Click on a bar to select ${barrierType} with that value.`}>
        [OPTIONAL] Use the filters below to select the {barrierType} that meet
        your needs. Click on a bar to select {barrierType} with that value.
        Click on the bar again to unselect. You can combine multiple values
        across multiple filters to select the {barrierType} that match ANY of
        those values within a filter and also have the values selected across
        ALL filters.
      </HelpText>

        {filterConfig.map(filter => (
          <Filter key={filter.field} {...filter} />
        ))}
      </Content>

      <Footer>
        <StartOverButton />

        <SubmitButton disabled={filteredCount === 0} onClick={onSubmit} label={`Prioritize ${barrierType}`} />
      </Footer>
    </Wrapper>
  )
}

Filters.propTypes = {
  onBack: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default Filters

// function FiltersList({
//   layer,
//   type,
//   dimensions,
//   filters,
//   counts,
//   totalCount,
//   summaryUnits,
//   setFilter: handleSetFilter,
//   resetFilters,
//   closedFilters,
//   toggleFilterClosed,
//   setMode,
//   fetchRanks,
// }) {
//   const handleResetFilters = () => {
//     resetFilters()
//   }

//   const hasFilters =
//     Object.values(filters.toJS()).reduce((out, v) => out + v.length, 0) > 0

//   return (
//     <React.Fragment>
//       <div id="SidebarHeader">
//         <button
//           className="link link-back"
//           type="button"
//           onClick={() => setMode('select')}
//         >
//           <span className="fa fa-reply" />
//           &nbsp; modify area of interest
//         </button>
//         <h4 className="title is-4 no-margin">Filter {type}</h4>
//         <div className="has-text-grey flex-container flex-justify-space-between">
//           <div>{formatNumber(totalCount, 0)} selected</div>
//           {hasFilters ? (
//             <button
//               className="link"
//               type="button"
//               onClick={handleResetFilters}
//               style={{ color: '#ee7d14' }}
//             >
//               <i className="fas fa-times-circle" />
//               &nbsp; reset filters
//             </button>
//           ) : null}
//         </div>
//       </div>
//       <div id="SidebarContent">
//         <p className="has-text-grey">
//           [OPTIONAL] Use the filters below to select the {type} that meet your
//           needs. Click on a bar to select {type} with that value. Click on the
//           bar again to unselect. You can combine multiple values across multiple
//           filters to select the {type} that match ANY of those values within a
//           filter and also have the values selected across ALL filters.
//         </p>
//         <div style={{ marginTop: '1rem' }}>
//           {dimensions.map(({ config }) => {
//             const { field } = config
//             return (
//               <Filter
//                 key={field}
//                 filterConfig={config}
//                 counts={counts.get(field)}
//                 filterValues={filters.get(field, Set())}
//                 closed={closedFilters.get(field, false)}
//                 onFilterChange={v => handleSetFilter(field, v)}
//                 toggleFilterClosed={v => toggleFilterClosed(field, v)}
//               />
//             )
//           })}
//         </div>
//       </div>

//       <div id="SidebarFooter">
//         <div className="flex-container flex-justify-center flex-align-center">
//           <StartOverButton />

//           <SubmitButton
//             disabled={totalCount === 0}
//             onClick={() =>
//               fetchRanks(type, layer, summaryUnits.toJS(), filters.toJS())
//             }
//             icon="search-location"
//             label={`Prioritize ${type}`}
//           />
//         </div>
//       </div>
//     </React.Fragment>
//   )
// }

// FiltersList.propTypes = {
//   type: PropTypes.string.isRequired,
//   layer: PropTypes.string.isRequired,

//   dimensions: ImmutablePropTypes.listOf(PropTypes.object).isRequired,
//   filters: ImmutablePropTypes.mapOf(
//     ImmutablePropTypes.setOf(
//       PropTypes.oneOfType([PropTypes.string, PropTypes.number])
//     )
//   ).isRequired,
//   counts: ImmutablePropTypes.mapOf(ImmutablePropTypes.mapOf(PropTypes.number))
//     .isRequired,
//   totalCount: PropTypes.number.isRequired,

//   closedFilters: ImmutablePropTypes.mapOf(PropTypes.bool).isRequired,

//   summaryUnits: ImmutablePropTypes.set.isRequired,
//   setFilter: PropTypes.func.isRequired,
//   resetFilters: PropTypes.func.isRequired,
//   toggleFilterClosed: PropTypes.func.isRequired,
//   setMode: PropTypes.func.isRequired,
//   fetchRanks: PropTypes.func.isRequired,
// }
// const mapStateToProps = globalState => {
//   const state = globalState.get('priority')
//   const crossfilter = globalState.get('crossfilter')

//   return {
//     type: state.get('type'),
//     layer: state.get('layer'),
//     closedFilters: state.get('closedFilters'),
//     summaryUnits: state.get('summaryUnits'),

//     dimensions: crossfilter.get('dimensions'),
//     counts: crossfilter.get('dimensionCounts'),
//     totalCount: crossfilter.get('filteredCount'),
//     filters: crossfilter.get('filters'),
//   }
// }

// export default connect(
//   mapStateToProps,
//   { setFilter, resetFilters: reset, ...actions }
// )(FiltersList)
