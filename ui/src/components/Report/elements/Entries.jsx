import React from 'react'
import PropTypes from 'prop-types'
import { View } from '@react-pdf/renderer'

const firstChildCSS = {
  paddingLeft: '6pt',
  paddingRight: '6pt',
}
const css = {
  ...firstChildCSS,
  marginTop: '6pt',
  paddingTop: '4pt',
  borderTop: '1px solid #ebedee',
}

const Entries = ({ children, style }) => {
  if (children && children.length) {
    return (
      <View style={style}>
        {children.map((child, i) =>
          child !== null ? (
            <View key={i} style={i > 0 ? css : firstChildCSS}>
              {child}
            </View>
          ) : null
        )}
      </View>
    )
  }

  // children is a node and not a list
  if (children) {
    return <View style={style}>{children}</View>
  }
  return null
}

Entries.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node),
  ]).isRequired,
  style: PropTypes.object,
}

Entries.defaultProps = {
  style: {},
}

export default Entries
