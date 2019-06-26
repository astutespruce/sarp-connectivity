import React, { memo } from 'react'
import PropTypes from 'prop-types'

import styled, { themeGet } from 'style'
import { STATE_FIPS } from '../../../config/constants'

const PREFIXES = {
  ECO3: 'Level 3',
  ECO4: 'Level 4',
}

const Wrapper = styled.li`
  padding: 0.5em;
  margin: 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  line-height: 1.2;

  &:hover {
    background-color: ${themeGet('colors.primary.100')};
  }
`

const Suffix = styled.span`
  margin-left: 0.5em;
  font-size: 0.75em;
  color: ${themeGet('colors.grey.600')};
  white-space: nowrap;
  word-wrap: none;
`

const State = styled.div`
  color: ${themeGet('colors.grey.800')};
`

const ListItem = ({ id, name, state, layer, showID, onClick }) => {
  const stateLabels = state
    ? state
        .split(',')
        .map(s => STATE_FIPS[s])
        .sort()
        .join(', ')
    : ''

  return (
    <Wrapper onClick={onClick}>
      <b>{name}</b>
      {showID && (
        <Suffix>
          ({layer && `${PREFIXES[layer] || layer}: `}
          {id})
        </Suffix>
      )}

      {stateLabels && <State>{stateLabels}</State>}
    </Wrapper>
  )
}

ListItem.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  state: PropTypes.string,
  layer: PropTypes.string,
  showID: PropTypes.bool,
}

ListItem.defaultProps = {
  state: '',
  layer: '',
  showID: false,
}

export default memo(ListItem)
