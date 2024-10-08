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
  rankedDams,
  totalSmallBarriers,
  rankedSmallBarriers,
  rankedLargefishBarriersDams,
  rankedLargefishBarriersSmallBarriers,
  rankedSmallfishBarriersDams,
  rankedSmallfishBarriersSmallBarriers,
  totalRoadCrossings,
  unsurveyedRoadCrossings,
  showID,
  showCount,
  disabled,
  focused,
  onClick,
}) => {
  const node = useRef(null)

  const totalRoadBarriers = totalSmallBarriers + unsurveyedRoadCrossings
  const insufficientBarriers =
    totalSmallBarriers < 10 && unsurveyedRoadCrossings > 10

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
          warning = `no road/stream crossings have been assessed in this area (${formatNumber(
            totalRoadBarriers
          )} road / stream ${pluralize('crossing', totalRoadBarriers)})`
        } else if (rankedSmallBarriers === 0) {
          warning = `no road-related barriers available for prioritization (${formatNumber(
            totalRoadBarriers
          )} road / stream ${pluralize('crossing', totalRoadBarriers)})`
        } else if (insufficientBarriers) {
          const prefix =
            totalSmallBarriers === 0
              ? 'no assessed road/stream crossings'
              : `${formatNumber(
                  totalSmallBarriers
                )} assessed road/stream ${pluralize(
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
            rankedD
          )} and ${formatNumber(rankedSB)} ${pluralize(
            'likely barrier',
            rankedSB
          )} (${formatNumber(
            totalSmallBarriers
          )} assessed road/stream ${pluralize(
            'crossing',
            totalSmallBarriers
          )} of ${formatNumber(totalRoadBarriers)} road/stream ${pluralize(
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
          countMessage = `${formatNumber(totalRoadCrossings)} total road/stream ${pluralize(
            'crossing',
            totalRoadCrossings
          )}`
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

  const stateLabels =
    state && layer !== 'CongressionalDistrict'
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
  rankedDams: PropTypes.number,
  totalSmallBarriers: PropTypes.number,
  rankedSmallBarriers: PropTypes.number,
  rankedLargefishBarriersDams: PropTypes.number,
  rankedLargefishBarriersSmallBarriers: PropTypes.number,
  rankedSmallfishBarriersDams: PropTypes.number,
  rankedSmallfishBarriersSmallBarriers: PropTypes.number,
  totalRoadCrossings: PropTypes.number,
  unsurveyedRoadCrossings: PropTypes.number,
  showID: PropTypes.bool,
  showCount: PropTypes.bool,
  disabled: PropTypes.bool,
  focused: PropTypes.bool,
}

ListItem.defaultProps = {
  state: '',
  layer: '',
  rankedDams: 0,
  totalSmallBarriers: 0,
  rankedSmallBarriers: 0,
  rankedLargefishBarriersDams: 0,
  rankedLargefishBarriersSmallBarriers: 0,
  rankedSmallfishBarriersDams: 0,
  rankedSmallfishBarriersSmallBarriers: 0,
  totalRoadCrossings: 0,
  unsurveyedRoadCrossings: 0,
  showID: false,
  showCount: false,
  disabled: false,
  focused: false,
}

export default memo(ListItem)
