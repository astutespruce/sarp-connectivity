import React from 'react'
import PropTypes from 'prop-types'
import { Text } from '@react-pdf/renderer'

import Flex from './Flex'
import LegendSymbol from './LegendSymbol'

const LegendElement = ({ type, label, symbols, ...props }) => (
  <Flex style={{ alignItems: 'center', lineHeight: 1 }}>
    <Flex
      style={{
        width: 30,
        alignItems: symbols ? 'baseline' : 'center',
        flex: '0 0 auto',
        gap: 0,
      }}
    >
      {symbols ? (
        symbols.map((p, i) => (
          <LegendSymbol
            /* eslint-disable-next-line react/no-array-index-key */
            key={`${p.color}-${p.borderColor}-${i}`}
            type={type}
            {...p}
          />
        ))
      ) : (
        <LegendSymbol type={type} {...props} />
      )}
    </Flex>

    <Text style={{ flex: '1 1 auto', fontSize: 9 }}>{label}</Text>
  </Flex>
)

LegendElement.propTypes = {
  type: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  symbols: PropTypes.arrayOf(
    PropTypes.shape({
      color: PropTypes.string.isRequired,
      borderColor: PropTypes.string,
      borderWidth: PropTypes.number,
    })
  ),
}

LegendElement.defaultProps = {
  symbols: null,
}

export default LegendElement
