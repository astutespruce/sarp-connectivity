import React from 'react'
import { View, Text } from '@react-pdf/renderer'

import Link from './elements/Link'

const Footer = () => (
  <View
    fixed
    style={{
      position: 'absolute',
      display: 'flex',
      justifyContent: 'space-between',
      bottom: 20,
      left: '0.5in',
      right: '0.5in',
      color: '#7f8a93',
      fontSize: 10,
    }}
  >
    <Text
      style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
      }}
      fixed
    >
      Created by the{' '}
      <Link href="https://tool.aquaticbarriers.org/">
        <Text>National Aquatic Barrier Inventory & Prioritization Tool</Text>
      </Link>{' '}
      on {new Date().toLocaleDateString()}.
    </Text>
    <Text
      style={{
        position: 'absolute',
        bottom: 0,
        right: 0,
        left: 0,
        textAlign: 'right',
      }}
      fixed
      render={({ pageNumber, totalPages }) =>
        `page ${pageNumber} of ${totalPages}`
      }
    />
  </View>
)

export default Footer
