/* eslint-disable camelcase */
import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Button, Text } from 'theme-ui'

import { useBarrierType } from 'components/Data'
import { STATE_FIPS, STATES, barrierTypeLabels } from 'config'
import { formatNumber } from 'util/format'

const SummaryUnitListItem = ({ layer, unit, onDelete }) => {
  const { id } = unit
  const { ranked_dams = 0, ranked_small_barriers = 0 } = unit
  let { name = id } = unit

  if (layer === 'State') {
    name = STATES[id]
  }

  const barrierType = useBarrierType()

  const count = barrierType === 'dams' ? ranked_dams : ranked_small_barriers

  const handleDelete = () => onDelete(unit)

  return (
    <Flex
      as="li"
      sx={{
        bg: count === 0 ? '#bbbbbb26' : 'inherit',
        justifyContent: 'space-between',
        borderBottom: '1px solid #EEE',
        mx: '-1rem',
        px: '1rem',
        py: '0.5em',
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
          {layer === 'County' ? ` County, ${STATE_FIPS[id.slice(0, 2)]}` : null}
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

        <Text sx={{ fontSize: '0.9rem', color: 'grey.6' }}>
          ({formatNumber(count)} {barrierTypeLabels[barrierType]}
          {count === 0 ? ', not available for prioritization' : ''})
        </Text>
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
