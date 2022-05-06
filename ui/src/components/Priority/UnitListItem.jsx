/* eslint-disable camelcase */
import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Box, Flex, Button, Text } from 'theme-ui'

import { useBarrierType } from 'components/Data'
import { formatNumber } from 'util/format'
import {
  STATE_FIPS,
  STATES,
  barrierTypeLabels,
} from '../../../config/constants'

const SummaryUnitListItem = ({ layer, unit, onDelete }) => {
  const { id } = unit
  const { name = id, on_network_dams = 0, on_network_small_barriers = 0 } = unit

  const barrierType = useBarrierType()

  console.log('id', id)

  const count =
    barrierType === 'dams' ? on_network_dams : on_network_small_barriers

  const handleDelete = () => onDelete(unit)

  return (
    <Flex
      as="li"
      sx={{
        justifyContent: 'space-between',
        borderBottom: '1px solid #EEE',
        pb: '1em',
        '&:not(:first-of-type)': {
          mt: '1em',
        },
      }}
    >
      <Box sx={{ flex: '1 1 auto', mr: '1em' }}>
        <Text sx={{ fontSize: '1.25rem' }}>
          {name}
          {layer === 'County' ? `, ${STATE_FIPS[id.slice(0, 2)]}` : null}
        </Text>

        {layer === 'HUC6' || layer === 'HUC8' || layer === 'HUC12' ? (
          <Text sx={{ color: 'grey.8' }}>
            {layer}: {id}
          </Text>
        ) : null}

        <Text sx={{ fontSize: '0.9rem', color: 'grey.6' }}>
          ({formatNumber(count)} {barrierTypeLabels[barrierType]})
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
