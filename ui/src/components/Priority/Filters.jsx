import React, { useMemo } from 'react'
import PropTypes from 'prop-types'
import { ExclamationTriangle, TimesCircle } from '@emotion-icons/fa-solid'
import { Box, Flex, Heading, Text } from 'theme-ui'

import { useBarrierType } from 'components/Data'
import { Filter } from 'components/Filters'
import { useCrossfilter } from 'components/Crossfilter'
import { ExpandableParagraph } from 'components/Text'
import { formatNumber } from 'util/format'
import { splitArray } from 'util/data'

import BackLink from './BackLink'
import SubmitButton from './SubmitButton'
import StartOverButton from './StartOverButton'
import { barrierTypeLabels } from '../../../config/constants'

const Filters = ({ onBack, onSubmit }) => {
  const barrierType = useBarrierType()
  const barrierTypeLabel = barrierTypeLabels[barrierType]
  const { state, filterConfig, resetFilters } = useCrossfilter()

  const { filteredCount, hasFilters, emptyDimensions } = state

  const handleBack = () => {
    resetFilters()
    onBack()
  }

  const handleReset = () => {
    resetFilters()
  }

  const [visibleFilters, hiddenFilters] = useMemo(
    () =>
      splitArray(
        filterConfig,
        ({ field }) => emptyDimensions.indexOf(field) === -1
      ),
    [emptyDimensions, filterConfig]
  )

  return (
    <Flex
      sx={{
        flexDirection: 'column',
        height: '100%',
      }}
    >
      <Box
        sx={{
          py: '1rem',
          pr: '0.5rem',
          pl: '1rem',
          bg: '#f6f6f2',
          borderBottom: '1px solid #DDD',
          flex: '0 0 auto',
        }}
      >
        <BackLink label="modify area of interest" onClick={handleBack} />

        <Heading as="h3" sx={{ fontSize: '1.5rem' }}>
          Filter {barrierTypeLabel}
        </Heading>

        <Flex
          sx={{
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Text sx={{ color: 'grey.7' }}>
            {formatNumber(filteredCount, 0)} selected
          </Text>
          {hasFilters && (
            <Flex
              onClick={handleReset}
              sx={{
                alignItems: 'center',
                color: 'highlight',
                cursor: 'pointer',
              }}
            >
              <TimesCircle size="1em" />
              <Text sx={{ ml: '0.5rem' }}>reset filters</Text>
            </Flex>
          )}
        </Flex>
      </Box>

      <Box
        sx={{
          px: '1rem',
          pt: '0.5rem',
          overflowY: 'auto',
          overflowX: 'hidden',
          flex: '1 1 auto',
        }}
      >
        <Box sx={{ color: 'grey.7', fontSize: 2, mb: '0.5rem' }}>
          <ExpandableParagraph
            variant="help"
            snippet={`[OPTIONAL] Use the filters below to select the ${barrierTypeLabel} that meet
        your needs. Click on a bar to select ${barrierTypeLabel} with that value.`}
          >
            <Text variant="help" sx={{ display: 'inline' }}>
              [OPTIONAL] Use the filters below to select the {barrierType} that
              meet your needs. Click on a bar to select {barrierType} with that
              value. Click on the bar again to unselect. You can combine
              multiple values across multiple filters to select the{' '}
              {barrierType} that match ANY of those values within a filter and
              also have the values selected across ALL filters.
            </Text>
          </ExpandableParagraph>
        </Box>

        {hiddenFilters.length > 0 ? (
          <Box
            sx={{
              pt: '0.5rem',
              pb: '1rem',
              borderTop: '1px solid',
              borderTopColor: 'grey.1',
            }}
          >
            <Text variant="help" sx={{ fontSize: 0 }}>
              <Box sx={{ display: 'inline-block', mr: '0.5em' }}>
                <ExclamationTriangle size="1em" />
              </Box>
              The following filters do not have sufficient unique values to
              support using them in this area:{' '}
              {hiddenFilters.map(({ title }) => title).join(', ')}.
            </Text>
          </Box>
        ) : null}

        {visibleFilters.map((filter) => (
          <Filter key={filter.field} {...filter} />
        ))}
      </Box>

      <Flex
        sx={{
          flex: '0 0 auto',
          justifyContent: 'space-between',
          alignItems: 'center',
          p: '1rem',
          bg: '#f6f6f2',
          borderTop: '1px solid #DDD',
        }}
      >
        <StartOverButton />

        <SubmitButton
          disabled={filteredCount === 0}
          onClick={onSubmit}
          label={`Prioritize ${barrierTypeLabel}`}
        />
      </Flex>
    </Flex>
  )
}

Filters.propTypes = {
  onBack: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default Filters
