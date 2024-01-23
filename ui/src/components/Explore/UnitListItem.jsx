import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Button, Text } from 'theme-ui'

import { STATE_FIPS, STATES } from 'config'
import { OutboundLink } from 'components/Link'
import { formatNumber, pluralize } from 'util/format'

const UnitListItem = ({ barrierType, system, unit, ignore, onDelete }) => {
  const { id, layerId, dams = 0, totalSmallBarriers = 0, crossings = 0 } = unit
  let { name = id } = unit

  if (layerId === 'State') {
    name = STATES[id]
  }

  let count = 0
  let countMessage = null

  switch (barrierType) {
    case 'dams': {
      count = dams
      countMessage = `${formatNumber(dams)} ${pluralize('dam', dams)}`

      break
    }
    case 'small_barriers': {
      count = totalSmallBarriers

      countMessage = `${formatNumber(
        totalSmallBarriers
      )} assessed potential road-related ${pluralize(
        'barrier',
        totalSmallBarriers
      )} (out of ${formatNumber(crossings)} road/stream ${pluralize(
        'crossing',
        crossings
      )})`

      break
    }
    case 'combined_barriers': {
      count = dams + totalSmallBarriers

      countMessage = `${formatNumber(dams)} ${pluralize(
        'dam',
        dams
      )} and ${formatNumber(
        totalSmallBarriers
      )} assessed potential road-related ${pluralize(
        'barrier',
        totalSmallBarriers
      )} (out of ${formatNumber(crossings)} road/stream ${pluralize(
        'crossing',
        crossings
      )})`

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
        mx: '-1rem',
        px: '1rem',
        py: '0.5em',
        '&:not(:first-of-type)': {
          borderTop: '1px solid',
          borderTopColor: 'grey.1',
        },
        '&:last-of-type': {
          borderBottom: '1px solid',
          borderBottomColor: 'grey.1',
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
            fontSize: 1,
            fontWeight: count > 0 && !ignore ? 'bold' : 'inherit',
            fontStyle: count === 0 || ignore ? 'italic' : 'inherit',
            color: count === 0 || ignore ? 'grey.8' : 'inherit',
          }}
        >
          {name}

          {layerId === 'State' ? (
            <Text
              sx={{
                display: 'inline',
                fontWeight: 'normal',
                fontSize: 0,
                color: 'grey.7',
              }}
            >
              {' '}
              (
              <OutboundLink to={`/states/${id}`}>
                view state details
              </OutboundLink>
              )
            </Text>
          ) : null}

          {layerId === 'County'
            ? ` County, ${STATE_FIPS[id.slice(0, 2)]}`
            : null}
        </Text>

        {system === 'HUC' ? (
          <Text
            sx={{
              fontSize: 0,
              fontStyle: count === 0 ? 'italic' : 'inherit',
              color: count === 0 ? 'grey.8' : 'inherit',
            }}
          >
            {layerId}: {id}
          </Text>
        ) : null}

        {countMessage !== null ? (
          <Text variant="help" sx={{ fontSize: 0 }}>
            {countMessage}
            {ignore ? ' (already counted in larger selected area)' : null}
          </Text>
        ) : null}
      </Box>

      <Button variant="close" onClick={handleDelete}>
        &#10006;
      </Button>
    </Flex>
  )
}

UnitListItem.propTypes = {
  barrierType: PropTypes.string.isRequired,
  system: PropTypes.string.isRequired,
  unit: PropTypes.object.isRequired,
  ignore: PropTypes.bool,
  onDelete: PropTypes.func.isRequired,
}

UnitListItem.defaultProps = {
  ignore: false,
}

export default memo(UnitListItem)
