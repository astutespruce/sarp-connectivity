import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { FaLayerGroup, FaTimesCircle } from 'react-icons/fa'

import { Flex, Box } from 'components/Grid'
import { Checkbox } from 'components/Button'
import { useEffectSkipFirst } from 'util/hooks'
import styled, { themeGet } from 'style'
import { MapControlWrapper } from './styles'

const Wrapper = styled(MapControlWrapper)`
  top: 150px;
  right: 10px;
  line-height: 1;
  background-color: ${({ isOpen }) => (isOpen ? '#eee' : '#fff')};
  border: none;
  padding: 7px;
  z-index: 10000;
`

const Icon = styled(FaLayerGroup)`
  width: 1em;
  height: 1em;
  margin-top: 1px;
  cursor: pointer;
`

const Header = styled.span`
  margin: 0 0.5em;
  font-weight: bold;
  font-size: 0.9em;
  display: inline-block;
  vertical-align: top;
  margin-top: 4px;
  cursor: pointer;
`

const CloseIcon = styled(FaTimesCircle)`
  width: 1em;
  height: 1em;
  color: ${themeGet('colors.grey.500')};
  cursor: pointer;

  &:hover {
    color: ${themeGet('colors.grey.900')};
  }
`

const Content = styled(Box).attrs({ py: '1rem', px: '0.5rem' })`
  width: 16rem;
`

const Row = styled(Flex).attrs({ alignItems: 'flex-start' })`
  &:not(:first-of-type) {
    margin-top: 1rem;
  }

  & label {
    font-size: small !important;
    font-weight: normal !important;
  }
`

const DropDownLayerChooser = ({ options, onChange }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [checkboxState, setCheckboxState] = useState(() =>
    options.reduce((prev, { id }) => Object.assign(prev, { [id]: false }), {})
  )

  const toggle = () => {
    setIsOpen((prevIsOpen) => !prevIsOpen)
  }

  const toggleCheckbox = (id) => () => {
    setCheckboxState((prevState) => ({
      ...prevState,
      [id]: !prevState[id],
    }))
  }

  useEffectSkipFirst(() => {
    onChange(checkboxState)
  }, [checkboxState])

  return (
    <Wrapper isOpen={isOpen}>
      {isOpen ? (
        <>
          <Flex justifyContent="space-between" alignItems="center">
            <div>
              <Icon onClick={toggle} />
              <Header onClick={toggle}>Show / hide map layers</Header>
            </div>
            <CloseIcon onClick={toggle} />
          </Flex>
          <Content>
            {options.map(({ id, label: checkboxLabel }) => (
              <Row key={id}>
                <Checkbox
                  id={id}
                  checked={checkboxState[id]}
                  label={checkboxLabel}
                  onChange={toggleCheckbox(id)}
                />
              </Row>
            ))}
          </Content>
        </>
      ) : (
        <Icon onClick={toggle} title="Show / hide map layers" />
      )}
    </Wrapper>
  )
}

DropDownLayerChooser.propTypes = {
  options: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  onChange: PropTypes.func.isRequired,
}

export default memo(DropDownLayerChooser, () => true)
