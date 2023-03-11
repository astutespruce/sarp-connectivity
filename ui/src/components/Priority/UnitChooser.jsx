import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Heading, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { UnitSearch } from 'components/UnitSearch'
import { useBarrierType } from 'components/Data'
import { barrierTypeLabels } from 'config'
import { formatNumber, pluralize } from 'util/format'

import BackLink from './BackLink'
import StartOverButton from './StartOverButton'
import SubmitButton from './SubmitButton'
import UnitListItem from './UnitListItem'

export const getPluralLabel = (layer) => {
  switch (layer) {
    case 'State':
      return 'states'
    case 'County':
      return 'counties'
    case 'HUC6':
      return 'basins'
    case 'HUC8':
      return 'subbasins'
    case 'HUC10':
      return 'watersheds'
    case 'HUC12':
      return 'subwatersheds'
    default:
      return 'areas'
  }
}

// used by caller, not here
export const getSingularLabel = (layer) => {
  switch (layer) {
    case 'State':
      return 'state'
    case 'County':
      return 'county'
    case 'HUC6':
      return 'basin'
    case 'HUC8':
      return 'subbasin'
    case 'HUC10':
      return 'watershed'
    case 'HUC12':
      return 'subwatershed'
    default:
      return 'area'
  }
}

const UnitChooser = ({
  layer,
  summaryUnits,
  selectUnit,
  onBack,
  onSubmit,
  onStartOver,
}) => {
  const barrierType = useBarrierType()
  const barrierTypeLabel = barrierTypeLabels[barrierType]
  const [searchValue, setSearchValue] = useState('')

  const pluralLabel = getPluralLabel(layer)

  let offNetworkCount = 0
  let total = 0
  let countMessage = null
  if (summaryUnits.length > 0) {
    switch (barrierType) {
      case 'dams': {
        offNetworkCount = summaryUnits.reduce(
          (out, v) => out + (v.dams - v.ranked_dams),
          0
        )
        total = summaryUnits.reduce((out, v) => out + v.ranked_dams, 0)
        countMessage = `${formatNumber(total)} ${pluralize('dam', total)}`
        break
      }
      case 'small_barriers': {
        offNetworkCount = summaryUnits.reduce(
          (out, v) => out + (v.small_barriers - v.ranked_small_barriers),
          0
        )
        total = summaryUnits.reduce(
          (out, v) => out + v.ranked_small_barriers,
          0
        )
        countMessage = `${formatNumber(total)} road-related ${pluralize(
          'barrier',
          total
        )}`
        break
      }
      case 'combined_barriers': {
        offNetworkCount = summaryUnits.reduce(
          (out, v) =>
            out +
            (v.dams - v.ranked_dams) +
            (v.small_barriers - v.ranked_small_barriers),
          0
        )
        total = summaryUnits.reduce(
          (out, v) => out + v.ranked_dams + v.ranked_small_barriers,
          0
        )

        let dams = 0
        let smallBarriers = 0
        summaryUnits.forEach(({ ranked_dams, ranked_small_barriers }) => {
          dams += ranked_dams
          smallBarriers += ranked_small_barriers
        })

        countMessage = `${formatNumber(dams)} ${pluralize(
          'dam',
          dams
        )} and ${formatNumber(smallBarriers)} road-related ${pluralize(
          'barrier',
          smallBarriers
        )}`

        break
      }
      default: {
        break
      }
    }
  }

  const handleSearchChange = (value) => {
    setSearchValue(value)
  }

  const handleSearchSelect = (item) => {
    // rename fields
    selectUnit(item)
    setSearchValue('')
  }

  return (
    <Flex sx={{ flexDirection: 'column', height: '100%' }}>
      <Box
        sx={{
          flex: '0 0 auto',
          py: '1rem',
          pr: '0.5rem',
          pl: '1rem',
          borderBottom: '1px solid #DDD',
          bg: '#f6f6f2',
        }}
      >
        <BackLink label="choose a different type of area" onClick={onBack} />
        <Heading as="h3">Choose {pluralLabel}</Heading>
      </Box>
      <Box
        sx={{
          flex: '1 1 auto',
          p: '1rem',
          overflowY: 'auto',
          overflowX: 'hidden',
        }}
      >
        <Text
          variant="help"
          sx={{
            mt: '-0.5rem',
            pb: '1.5rem',
          }}
        >
          Select {summaryUnits.length > 0 ? 'additional' : ''} {pluralLabel} by
          clicking on them on the map or using the search below.
        </Text>

        {summaryUnits.length > 0 ? (
          <Box
            as="ul"
            sx={{
              m: '0 0 2rem 0',
              p: 0,
              listStyle: 'none',
            }}
          >
            {summaryUnits.map((unit) => (
              <UnitListItem
                key={unit.id}
                layer={layer}
                unit={unit}
                onDelete={() => selectUnit(unit)}
              />
            ))}
          </Box>
        ) : null}

        <UnitSearch
          barrierType={barrierType}
          layer={layer}
          value={searchValue}
          ignoreIds={
            summaryUnits && summaryUnits.length > 0
              ? new Set(summaryUnits.map(({ id }) => id))
              : null
          }
          showCount
          onChange={handleSearchChange}
          onSelect={handleSearchSelect}
        />

        {summaryUnits.length > 0 && offNetworkCount > 0 ? (
          <Text variant="help" sx={{ mt: '2rem', pb: '2rem' }}>
            Note: only {barrierTypeLabel} that have been evaluated for aquatic
            network connectivity are available for prioritization. There are{' '}
            <b>{formatNumber(offNetworkCount, 0)}</b> {barrierTypeLabel} not
            available for prioritization in your selected area.
          </Text>
        ) : null}

        {!(layer === 'State' || layer === 'County') ? (
          <Text variant="help" sx={{ pt: '2rem' }}>
            <ExclamationTriangle
              size="1em"
              style={{ marginRight: '0.25rem' }}
            />
            Note: You can choose from {pluralLabel} outside the highlighted
            states, but the barriers inventory is more complete only where{' '}
            {pluralLabel} overlap the highlighted states.
          </Text>
        ) : null}
      </Box>

      <Box
        sx={{
          flex: '0 0 auto',
          pt: '0.5rem',
          pb: '1rem',
          px: '1rem',
          borderTop: '1px solid #DDD',
          bg: '#f6f6f2',
        }}
      >
        {countMessage !== null ? (
          <Text sx={{ fontSize: 1, textAlign: 'right' }}>
            selected: {countMessage}
          </Text>
        ) : null}

        <Flex
          sx={{
            alignItems: 'center',
            justifyContent: 'space-between',
            mt: '1rem',
          }}
        >
          <StartOverButton onStartOver={onStartOver} />

          <SubmitButton
            disabled={summaryUnits.size === 0 || total === 0}
            onClick={onSubmit}
            label="Configure filters"
            title={
              summaryUnits.size === 0 || total === 0
                ? `you must select at least one area that has ${barrierTypeLabel} available`
                : null
            }
          />
        </Flex>
      </Box>
    </Flex>
  )
}

UnitChooser.propTypes = {
  layer: PropTypes.string.isRequired,
  summaryUnits: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
    })
  ).isRequired,
  onBack: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onStartOver: PropTypes.func.isRequired,
  selectUnit: PropTypes.func.isRequired,
}

export default UnitChooser
