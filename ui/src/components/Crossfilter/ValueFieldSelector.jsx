import React, { useContext } from 'react'
import PropTypes from 'prop-types'

import { Flex } from 'components/Grid'
import { ToggleButton as BaseButton } from 'components/Button'
import styled, { themeGet } from 'style'

import { SET_VALUE_FIELD } from './Crossfilter'
import { Context } from './Context'

const Wrapper = styled(Flex).attrs({
  alignItems: 'center',
  justifyContent: 'center',
})``

const Label = styled.div`
  margin-right: 0.5em;
  color: ${themeGet('colors.grey.600')};
`

const ToggleButton = styled(BaseButton)`
  button {
    flex-grow: 1;
    padding: 4px 8px;
    font-size: smaller;
    font-weight: normal;
`

const ValueFieldSelector = ({ fields }) => {
  const { state, dispatch } = useContext(Context)

  const handleChange = field => {
    dispatch({
      type: SET_VALUE_FIELD,
      payload: { field },
    })
  }

  const options = fields.map(f => ({
    value: f,
    label: f === 'id' ? 'detectors' : f,
  }))

  return (
    <Wrapper>
      <Label>metric to display:</Label>
      <ToggleButton
        value={state.get('valueField')}
        options={options}
        onChange={handleChange}
      />
    </Wrapper>
  )
}

ValueFieldSelector.propTypes = {
  fields: PropTypes.arrayOf(PropTypes.string).isRequired,
}

export default ValueFieldSelector
