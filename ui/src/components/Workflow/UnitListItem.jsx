import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Button, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { useBarrierType } from 'components/Data'
import { STATE_FIPS, STATES, barrierTypeLabels } from 'config'
import { formatNumber, pluralize } from 'util/format'

const SummaryUnitListItem = ({ layer, unit, onDelete }) => {
  const {
    id,
    rankedDams = 0,
    totalSmallBarriers = 0,
    rankedSmallBarriers = 0,
    rankedLargefishBarriersDams = 0,
    rankedLargefishBarriersSmallBarriers = 0,
    rankedSmallfishBarriersDams = 0,
    rankedSmallfishBarriersSmallBarriers = 0,
    totalRoadCrossings = 0,
    unsurveyedRoadCrossings = 0,
  } = unit
  let { name = id } = unit

  const totalRoadBarriers = totalSmallBarriers + unsurveyedRoadCrossings
  const insufficientBarriers = totalSmallBarriers < 10 && totalRoadBarriers > 10

  if (layer === 'State') {
    name = STATES[id]
  }

  const barrierType = useBarrierType()

  let count = 0
  let warning = null
  let countMessage = null

  switch (barrierType) {
    case 'dams': {
      count = rankedDams
      if (rankedDams === 0) {
        warning = 'no dams available for prioritization'
      } else {
        countMessage = `${formatNumber(rankedDams)} ${pluralize(
          'dam',
          rankedDams
        )}`
      }

      break
    }
    case 'small_barriers': {
      count = rankedSmallBarriers
      if (totalSmallBarriers === 0) {
        warning = `no road/stream crossings (potential barriers) have been assessed in this area (${formatNumber(
          totalRoadBarriers
        )} road / stream ${pluralize('crossing', totalRoadBarriers)})`
      } else if (rankedSmallBarriers === 0) {
        warning = `no road-related barriers available for prioritization (${formatNumber(
          totalRoadBarriers
        )} road / stream ${pluralize('crossing', totalRoadBarriers)})`
      } else if (insufficientBarriers) {
        const prefix =
          totalSmallBarriers === 0
            ? 'no road/stream crossings (potential barriers)'
            : `${formatNumber(totalSmallBarriers)} road/stream ${pluralize(
                'crossing',
                totalSmallBarriers
              )} (${formatNumber(rankedSmallBarriers)} likely ${pluralize(
                'barrier',
                rankedSmallBarriers
              )})`
        warning = `${prefix} ${
          rankedSmallBarriers === 1 ? 'has' : 'have'
        } been assessed out of ${formatNumber(
          totalRoadBarriers
        )} total road / stream ${pluralize(
          'crossing',
          totalRoadBarriers
        )}; this may not result in useful priorities`
      } else {
        countMessage = `${formatNumber(rankedSmallBarriers)} ${pluralize(
          'barrier',
          rankedSmallBarriers
        )} (${formatNumber(
          totalSmallBarriers
        )} assessed road/stream ${pluralize(
          'crossing',
          totalSmallBarriers
        )} of ${formatNumber(totalRoadBarriers)} total road/stream ${pluralize(
          'crossing',
          totalRoadBarriers
        )})`
      }

      break
    }
    case 'combined_barriers':
    case 'largefish_barriers':
    case 'smallfish_barriers': {
      // extract counts specific to network type
      let rankedD = 0
      let rankedSB = 0
      if (barrierType === 'combined_barriers') {
        rankedD = rankedDams
        rankedSB = rankedSmallBarriers
      } else if (barrierType === 'largefish_barriers') {
        rankedD = rankedLargefishBarriersDams
        rankedSB = rankedLargefishBarriersSmallBarriers
      } else if (barrierType === 'smallfish_barriers') {
        rankedD = rankedSmallfishBarriersDams
        rankedSB = rankedSmallfishBarriersSmallBarriers
      }

      count = rankedD + rankedSB

      if (count === 0) {
        warning = `no ${barrierTypeLabels[barrierType]} available for prioritization`
      } else if (rankedD > 0 && insufficientBarriers) {
        const prefix =
          totalSmallBarriers === 0
            ? 'no assessed road/stream crossings'
            : `${formatNumber(
                totalSmallBarriers
              )} assessed road/stream ${pluralize(
                'crossing',
                totalSmallBarriers
              )} (${formatNumber(rankedSB)} likely ${pluralize(
                'barrier',
                rankedSB
              )})`
        warning = `${prefix} ${
          totalSmallBarriers === 1 ? 'has' : 'have'
        } been assessed out of ${formatNumber(
          totalRoadBarriers
        )} total road / stream ${pluralize(
          'crossing',
          totalRoadBarriers
        )}; this may not result in useful priorities`

        countMessage = `${formatNumber(rankedD)} ${pluralize('dam', rankedD)}`
      } else if (rankedD > 0) {
        countMessage = `${formatNumber(rankedD)} ${pluralize(
          'dam',
          rankedDams
        )} and ${formatNumber(rankedSB)} road-related ${pluralize(
          'barrier',
          rankedSB
        )} (${formatNumber(
          totalSmallBarriers
        )} assessed road/stream ${pluralize(
          'crossing',
          totalSmallBarriers
        )} of ${formatNumber(totalRoadBarriers)} total road/stream ${pluralize(
          'crossing',
          totalRoadBarriers
        )})`
      }

      break
    }
    case 'road_crossings': {
      count = totalRoadCrossings

      if (totalRoadCrossings === 0) {
        warning = `no road/stream crossings have been mapped in this area`
      } else {
        countMessage = `${formatNumber(totalRoadCrossings)} road/stream ${pluralize(
          'crossing',
          totalRoadCrossings
        )} (${formatNumber(
          unsurveyedRoadCrossings
        )} have not yet been surveyed; ${formatNumber(totalSmallBarriers)} potential road-related
        ${pluralize('barrier', totalSmallBarriers)}
        have been inventoried)`
      }
      break
    }
    default: {
      break
    }
  }

  const handleDelete = () => onDelete(unit)

  return (
    <Flex
      as="li"
      sx={{
        justifyContent: 'space-between',
        borderBottom: '1px solid',
        borderBottomColor: 'grey.1',
        mx: '-1rem',
        px: '1rem',
        py: '0.5em',
        '&:first-of-type': {
          borderTop: '1px solid',
          borderTopColor: 'grey.1',
        },
      }}
    >
      <Box
        sx={{
          flex: '1 1 auto',
          mr: '1em',
        }}
      >
        <Text
          sx={{
            fontSize: '1rem',
            fontWeight: count > 0 ? 'bold' : 'inherit',
            fontStyle: count === 0 ? 'italic' : 'inherit',
            color: count === 0 ? 'grey.8' : 'inherit',
          }}
        >
          {name}
          {layer === 'County' ? `, ${STATE_FIPS[id.slice(0, 2)]}` : null}
        </Text>

        {layer === 'HUC6' || layer === 'HUC8' || layer === 'HUC12' ? (
          <Text
            sx={{
              fontSize: '0.9rem',
              fontStyle: count === 0 ? 'italic' : 'inherit',
              color: count === 0 ? 'grey.8' : 'inherit',
            }}
          >
            {layer}: {id}
          </Text>
        ) : null}

        {countMessage !== null ? (
          <Text variant="help">{countMessage}</Text>
        ) : null}

        {warning !== null ? (
          <Flex
            sx={{
              mt: '0.25rem',
              color: 'highlight',
              fontSize: 1,
              gap: '0.5rem',
              lineHeight: 1.1,
            }}
          >
            <Box sx={{ flex: '0 0 auto' }}>
              <ExclamationTriangle size="1.5em" />
            </Box>
            <Text sx={{ flex: '1 1 auto' }}>{warning}</Text>
          </Flex>
        ) : null}
      </Box>

      <Button variant="close" onClick={handleDelete}>
        &#10006;
      </Button>
    </Flex>
  )
}
SummaryUnitListItem.propTypes = {
  layer: PropTypes.string.isRequired,
  unit: PropTypes.object.isRequired,
  onDelete: PropTypes.func.isRequired,
}

export default memo(SummaryUnitListItem)
