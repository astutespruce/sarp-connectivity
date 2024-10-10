import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { siteMetadata } from 'config'
import { Link, Section } from './elements'

const { version: dataVersion } = siteMetadata

const Contact = ({ barrierType, sarpid, style }) => (
  <View
    wrap={false}
    style={{
      ...style,
      backgroundColor: '#ebedee',
      borderRadius: 6,
      padding: 12,
    }}
  >
    <Section title="Contact us">
      <Text style={{ padding: '0 12pt' }}>
        If you see an issue with the details for this barrier, please{' '}
        <Link
          href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
            barrierType === 'dams' ? 'dam' : 'road-related barrier'
          }: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
        >
          <Text>let us know!</Text>
        </Link>
        {'\n\n'}
        If you would like more information about this barrier or the aquatic
        connectivity analysis results presented above, please{' '}
        <Link href="mailto:Kat@southeastaquatics.net">
          <Text>contact us</Text>
        </Link>
        .
      </Text>
    </Section>
  </View>
)

Contact.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
  style: PropTypes.object,
}

Contact.defaultProps = {
  style: {},
}

export default Contact
