import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { LayerGroup } from '@emotion-icons/fa-solid'
import { Box, Button, Flex, Text } from 'theme-ui'

import { Checkbox } from 'components/Button'
import { useEffectSkipFirst } from 'util/hooks'

const controlCSS = {
  position: 'absolute',
  top: '120px',
  right: '10px',
  lineHeight: 1,
  bg: '#FFF',
  border: 'none',
  borderRadius: '4px',
  boxShadow: '0 0 0 2px rgba(0,0,0,0.1)',
  padding: '7px',
  zIndex: 2000,
}

const DropDownLayerChooser = ({ options, onChange }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [checkboxState, setCheckboxState] = useState(() =>
    options.reduce((prev, { id }) => Object.assign(prev, { [id]: false }), {})
  )

  const handleToggle = () => {
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

  if (!isOpen) {
    return (
      <Box
        sx={{
          ...controlCSS,
          cursor: 'pointer',
          width: '29px',
          '&:hover': {
            bg: '#EEE',
          },
        }}
        onClick={handleToggle}
        title="Show / hide map layers"
      >
        <LayerGroup size="1em" />
      </Box>
    )
  }

  return (
    <Box
      sx={{
        ...controlCSS,
        zIndex: 20000,
        border: '1px solid #AAA',
        boxShadow: '1px 1px 8px #333',
      }}
    >
      <Flex sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
        <Box sx={{ flex: '0 0 auto' }} onClick={handleToggle}>
          <LayerGroup size="1em" />
        </Box>
        <Text
          onClick={handleToggle}
          sx={{
            mx: '0.5em',
            flex: '1 1 auto',
            fontWeight: 'bold',
            fontSize: 1,
            cursor: 'pointer',
          }}
        >
          Show / hide map layers
        </Text>

        <Button
          variant="close"
          sx={{ fontSize: '0.8rem', height: '0.9rem', width: '0.9rem' }}
          onClick={handleToggle}
        >
          &#10006;
        </Button>
      </Flex>
      <Box
        sx={{
          mt: '1rem',
          maxWidth: '16rem',
          label: {
            fontSize: 1,
            lineHeight: 1.3,
          },
          '&>div + div': {
            mt: '0.5em',
          },
        }}
      >
        {options.map(({ id, label: checkboxLabel }) => (
          <Box key={id}>
            <Checkbox
              id={id}
              checked={checkboxState[id]}
              label={checkboxLabel}
              onChange={toggleCheckbox(id)}
            />
          </Box>
        ))}
      </Box>
    </Box>
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
