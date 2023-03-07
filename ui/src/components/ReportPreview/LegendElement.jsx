import React from 'react'
import PropTypes from 'prop-types'
import { Flex, Text } from 'theme-ui'

import LegendSymbol from './LegendSymbol'

const LegendElement = ({ label, type, symbols, sx, ...props }) => (
  <Flex sx={sx}>
    <Flex
      sx={{
        flex: '0 0 18px',
        alignItems: symbols ? 'baseline' : 'center',
        width: '12px',
        mr: '0.5rem',
        gap: '3px',
      }}
    >
      {symbols ? (
        symbols.map((p, i) => (
          <LegendSymbol
            key={`${p.color}-${p.borderColor}-${i}`}
            type={type}
            {...p}
          />
        ))
      ) : (
        <LegendSymbol type={type} {...props} />
      )}
    </Flex>

    <Text sx={{ ml: '0.5rem' }}>{label}</Text>
  </Flex>
)

LegendElement.propTypes = {
  label: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  symbols: PropTypes.arrayOf(
    PropTypes.shape({
      color: PropTypes.string.isRequired,
      borderColor: PropTypes.string,
      borderWidth: PropTypes.number,
    })
  ),
  sx: PropTypes.object,
}

LegendElement.defaultProps = {
  symbols: null,
  sx: null,
}

export default LegendElement
