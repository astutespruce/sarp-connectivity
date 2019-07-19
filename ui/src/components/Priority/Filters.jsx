import React from 'react'
import PropTypes from 'prop-types'
import { FaTimesCircle } from 'react-icons/fa'

import { useBarrierType } from 'components/Data'
import { Filter } from 'components/Filters'
import { useCrossfilter } from 'components/Crossfilter'
import { ExpandableParagraph } from 'components/Text'
import { Flex } from 'components/Grid'

import styled, { themeGet } from 'style'
import { formatNumber } from 'util/format'

import BackLink from './BackLink'
import SubmitButton from './SubmitButton'
import StartOverButton from './StartOverButton'
import { Wrapper, Header, Footer, Title, Content } from './styles'


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
        <HelpText
          snippet={`[OPTIONAL] Use the filters below to select the ${barrierType} that meet
        your needs. Click on a bar to select ${barrierType} with that value.`}
        >
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

        <SubmitButton
          disabled={filteredCount === 0}
          onClick={onSubmit}
          label={`Prioritize ${barrierType}`}
        />
      </Footer>
    </Wrapper>
  )
}

Filters.propTypes = {
  onBack: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default Filters
