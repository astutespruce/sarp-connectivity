import React, { useEffect, useRef, memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Text } from 'theme-ui'
import { ExclamationTriangle } from '@emotion-icons/fa-solid'

import { STATES, barrierTypeLabels } from 'config'
import { formatNumber, pluralize } from 'util/format'

const ListItem = ({
  barrierType,
  id,
  name,
  state,
  layer,
  ranked_dams: rankedDams,
  total_small_barriers: totalSmallBarriers,
  ranked_small_barriers: rankedSmallBarriers,
  ranked_largefish_barriers_dams: rankedLargefishBarriersDams,
  ranked_largefish_barriers_small_barriers:
    rankedLargefishBarriersSmallBarriers,
  ranked_smallfish_barriers_dams: rankedSmallfishBarriersDams,
  ranked_smallfish_barriers_small_barriers:
    rankedSmallfishBarriersSmallBarriers,
  crossings,
  showID,
  showCount,
  disabled,
  focused,
  onClick,
}) => {
  const node = useRef(null)

  const insufficientBarriers = totalSmallBarriers < 10 && crossings > 10

  let count = 0
  let warning = null
  let countMessage = null

  if (showCount && !disabled) {
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
          warning = `no potential road-related barriers have been assessed in this area (${formatNumber(
            crossings
          )} road / stream ${pluralize('crossing', crossings)})`
        } else if (rankedSmallBarriers === 0) {
          warning = `no road-related barriers available for prioritization (${formatNumber(
            crossings
          )} road / stream ${pluralize('crossing', crossings)})`
        } else if (insufficientBarriers) {
          const prefix =
            totalSmallBarriers === 0
              ? 'no potential road-related barriers'
              : `${formatNumber(
                  totalSmallBarriers
                )} potential road-related ${pluralize(
                  'barrier',
                  totalSmallBarriers
                )} (${formatNumber(rankedSmallBarriers)} likely ${pluralize(
                  'barrier',
                  rankedSmallBarriers
                )})`
          warning = `${prefix} ${
            rankedSmallBarriers === 1 ? 'has' : 'have'
          } been assessed out of ${formatNumber(
            crossings
          )} road / stream ${pluralize(
            'crossing',
            crossings
          )}; this may not result in useful priorities`
        } else {
          countMessage = `${formatNumber(rankedSmallBarriers)} ${pluralize(
            'barrier',
            rankedSmallBarriers
          )} (${formatNumber(
            totalSmallBarriers
          )} assessed potential road-related ${pluralize(
            'barrier',
            totalSmallBarriers
          )} of ${formatNumber(crossings)} road/stream ${pluralize(
            'crossing',
            crossings
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
              ? 'no potential road-related barriers'
              : `${formatNumber(
                  totalSmallBarriers
                )} potential road-related ${pluralize(
                  'barrier',
                  totalSmallBarriers
                )} (${formatNumber(rankedSB)} likely ${pluralize(
                  'barrier',
                  rankedSB
                )})`
          warning = `${prefix} ${
            totalSmallBarriers === 1 ? 'has' : 'have'
          } been assessed out of ${formatNumber(
            crossings
          )} road / stream ${pluralize(
            'crossing',
            crossings
          )}; this may not result in useful priorities`

          countMessage = `${formatNumber(rankedD)} ${pluralize('dam', rankedD)}`
        } else if (rankedD > 0) {
          countMessage = `${formatNumber(rankedD)} ${pluralize(
            'dam',
            rankedD
          )} and ${formatNumber(rankedSB)} ${pluralize(
            'likely barrier',
            rankedSB
          )} (${formatNumber(
            totalSmallBarriers
          )} assessed potential road-related ${pluralize(
            'barrier',
            totalSmallBarriers
          )} of ${formatNumber(crossings)} road/stream ${pluralize(
            'crossing',
            crossings
          )})`
        }

        break
      }
      default: {
        break
      }
    }
  }

  useEffect(() => {
    if (node.current && focused) {
      node.current.focus()
    }
  }, [focused])

  const stateLabels = state
    ? state
        .split(',')
        .map((s) => STATES[s])
        .sort()
        .join(', ')
    : ''

  return (
    <Box
      ref={node}
      as="li"
      onClick={!disabled ? onClick : null}
      tabIndex={0}
      sx={{
        p: '0.5em',
        m: '0px',
        borderBottom: '1px solid #EEE',
        cursor: disabled ? 'not-allowed' : 'pointer',
        lineHeight: 1.2,
        '&:hover': {
          bg: 'grey.0',
        },
        fontStyle: disabled ? 'italic' : 'inherit',
        color: disabled ? 'grey.7' : 'inherit',
        bg: disabled ? 'grey.0' : 'inherit',
      }}
    >
      <Box sx={{ fontWeight: !disabled ? 'bold' : 'inherit' }}>
        {name}

        {stateLabels ? (
          <Text sx={{ display: 'inline', fontSize: 1, ml: '0.5rem' }}>
            ({stateLabels})
          </Text>
        ) : null}

        {disabled ? (
          <Text sx={{ fontSize: 0, display: 'inline-block', ml: '0.25rem' }}>
            (already selected)
          </Text>
        ) : null}
      </Box>
      {showID ? (
        <Box
          sx={{
            fontSize: 0,
            color: 'grey.7',
            whiteSpace: 'nowrap',
            wordWrap: 'none',
          }}
        >
          {layer ? `${layer}: ` : null}
          {id}
        </Box>
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
  )
}

ListItem.propTypes = {
  barrierType: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  state: PropTypes.string,
  layer: PropTypes.string,
  ranked_dams: PropTypes.number,
  total_small_barriers: PropTypes.number,
  ranked_small_barriers: PropTypes.number,
  ranked_largefish_barriers_dams: PropTypes.number,
  ranked_largefish_barriers_small_barriers: PropTypes.number,
  ranked_smallfish_barriers_dams: PropTypes.number,
  ranked_smallfish_barriers_small_barriers: PropTypes.number,
  crossings: PropTypes.number,
  showID: PropTypes.bool,
  showCount: PropTypes.bool,
  disabled: PropTypes.bool,
  focused: PropTypes.bool,
}

ListItem.defaultProps = {
  state: '',
  layer: '',
  ranked_dams: 0,
  total_small_barriers: 0,
  ranked_small_barriers: 0,
  ranked_largefish_barriers_dams: 0,
  ranked_largefish_barriers_small_barriers: 0,
  ranked_smallfish_barriers_dams: 0,
  ranked_smallfish_barriers_small_barriers: 0,
  crossings: 0,
  showID: false,
  showCount: false,
  disabled: false,
  focused: false,
}

export default memo(ListItem)
