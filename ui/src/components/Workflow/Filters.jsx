import React from 'react'
import PropTypes from 'prop-types'
import { TimesCircle } from '@emotion-icons/fa-solid'
import { Box, Flex, Heading, Text } from 'theme-ui'
import { op } from 'arquero'

import { barrierTypeLabels } from 'config'
import { useCrossfilter } from 'components/Crossfilter'
import { useBarrierType } from 'components/Data'
import { FilterGroup } from 'components/Filters'
import { ExpandableParagraph } from 'components/Text'
import { reduceToObject } from 'util/data'
import { formatNumber, pluralize } from 'util/format'

import BackLink from './BackLink'
import StartOverButton from './StartOverButton'

const Filters = ({ onBack, onStartOver, SubmitButton }) => {
  const barrierType = useBarrierType()
  const barrierTypeLabel = barrierTypeLabels[barrierType]
  const {
    state: { filteredData: data, filteredCount, hasFilters, emptyGroups },
    filterConfig,
    resetFilters,
  } = useCrossfilter()

  const handleBack = () => {
    resetFilters()
    onBack()
  }

  const handleReset = () => {
    resetFilters()
  }

  let countMessage = null
  switch (barrierType) {
    case 'dams': {
      countMessage = `${formatNumber(filteredCount)} ${pluralize(
        'dam',
        filteredCount
      )}`
      break
    }
    case 'small_barriers': {
      countMessage = `${formatNumber(filteredCount)} road-related ${pluralize(
        'barrier',
        filteredCount
      )}`
      break
    }
    case 'combined_barriers':
    case 'largefish_barriers':
    case 'smallfish_barriers': {
      const { dams = 0, small_barriers: smallBarriers = 0 } = data
        .groupby('barriertype')
        .rollup({ _count: (d) => op.sum(d._count) })
        .derive({ row: op.row_object() })
        .array('row')
        .reduce(...reduceToObject('barriertype', (d) => d._count))

      countMessage = `${formatNumber(dams || 0)} ${pluralize(
        'dam',
        dams
      )} and ${formatNumber(smallBarriers)} road-related ${pluralize(
        'barrier',
        smallBarriers
      )}`
      break
    }
    case 'road_crossings': {
      countMessage = `${formatNumber(filteredCount)} road/stream ${pluralize(
        'crossing',
        filteredCount
      )}`
      break
    }
    default: {
      console.error(`${barrierType} not handled in switch statement`)
      break
    }
  }

  return (
    <Flex
      sx={{
        flexDirection: 'column',
        height: '100%',
      }}
    >
      <Box
        sx={{
          pt: '1rem',
          pb: '0.25rem',
          pr: '0.5rem',
          pl: '1rem',
          bg: '#f6f6f2',
          borderBottom: '1px solid #DDD',
          flex: '0 0 auto',
        }}
      >
        <BackLink label="modify area of interest" onClick={handleBack} />

        <Flex sx={{ justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <Heading as="h3" sx={{ fontSize: '1.5rem', flex: '1 1 auto' }}>
            Filter {barrierTypeLabel}
          </Heading>
          <Flex
            onClick={handleReset}
            sx={{
              flex: '0 0 auto',
              justifyContent: 'flex-end',
              alignItems: 'center',
              visibility: hasFilters ? 'visible' : 'hidden',
              color: 'highlight',
              cursor: 'pointer',
            }}
          >
            <TimesCircle size="1em" />
            <Text sx={{ ml: '0.5rem' }}>reset filters</Text>
          </Flex>
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
        <Box sx={{ color: 'grey.7', fontSize: 1, mb: '0.5rem' }}>
          <ExpandableParagraph
            variant="help"
            snippet={`[OPTIONAL] Use the filters below to select the ${barrierTypeLabel} that meet
        your needs. Click on a bar to select ${barrierTypeLabel} with that value.`}
          >
            <Text variant="help" sx={{ display: 'inline' }}>
              [OPTIONAL] Use the filters below to select the {barrierTypeLabel}{' '}
              that meet your needs. Click on a bar to select {barrierTypeLabel}{' '}
              with that value. Click on the bar again to unselect. You can
              combine multiple values across multiple filters to select the{' '}
              {barrierTypeLabel} that match ANY of those values within a filter
              and also have the values selected across ALL filters.
            </Text>
          </ExpandableParagraph>
        </Box>

        <Box>
          {filterConfig
            .filter(({ id }) => !emptyGroups.has(id))
            .map((group) => (
              <FilterGroup key={group.id} {...group} />
            ))}
        </Box>
      </Box>

      <Box
        sx={{
          flex: '0 0 auto',
          pt: '0.5rem',
          pb: '1rem',
          px: '1rem',
          bg: '#f6f6f2',
          borderTop: '1px solid #DDD',
        }}
      >
        <Text sx={{ fontSize: 1, textAlign: 'right' }}>
          selected: {countMessage}
        </Text>

        <Flex
          sx={{
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: '1rem',
          }}
        >
          <StartOverButton onStartOver={onStartOver} />

          {SubmitButton}
        </Flex>
      </Box>
    </Flex>
  )
}

Filters.propTypes = {
  onBack: PropTypes.func.isRequired,
  onStartOver: PropTypes.func.isRequired,
  SubmitButton: PropTypes.node.isRequired,
}

export default Filters
