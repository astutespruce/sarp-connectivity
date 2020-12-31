/* eslint-disable camelcase */
import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { useBarrierType } from 'components/Data'
import { Text } from 'components/Text'
import { Flex } from 'components/Grid'
import { CloseButton } from 'components/Button'
import { formatNumber } from 'util/format'
import styled, { themeGet } from 'style'
import { STATE_FIPS } from '../../../config/constants'

const Wrapper = styled(Flex).attrs({
  as: 'li',
  justifyContent: 'space-between',
})`
  line-height: 1.4;
  border-bottom: 1px solid #eee;
  padding-bottom: 1em;

  &:not(:first-of-type) {
    margin-top: 1em;
  }
`

const Content = styled.div`
  flex: 1 1 auto;
  margin-right: 1em;
`

const Name = styled(Text).attrs({ fontSize: '1.25rem' })``

const HUC = styled.div`
  color: ${themeGet('colors.grey.800')};
`

const Count = styled.div`
  font-size: 0.9rem;
  color: ${themeGet('colors.grey.600')};
`

const SummaryUnitListItem = ({ layer, unit, onDelete }) => {
  const { id } = unit
  const { name = id, on_network_dams = 0, on_network_barriers = 0 } = unit

  const barrierType = useBarrierType()

  const count = barrierType === 'dams' ? on_network_dams : on_network_barriers

  const handleDelete = () => onDelete(unit)

  return (
    <Wrapper>
      <Content>
        <Name>
          {name}
          {layer === 'County' ? `, ${STATE_FIPS[id.slice(0, 2)]}` : null}
        </Name>

        {layer === 'HUC6' || layer === 'HUC8' || layer === 'HUC12' ? (
          <HUC>
            {layer}: {id}
          </HUC>
        ) : null}

        <Count>
          ({formatNumber(count)} {barrierType})
        </Count>
      </Content>

      <CloseButton onClick={handleDelete} />
    </Wrapper>
  )
}
SummaryUnitListItem.propTypes = {
  layer: PropTypes.string.isRequired,
  unit: PropTypes.object.isRequired,
  onDelete: PropTypes.func.isRequired,
}

export default memo(SummaryUnitListItem)
