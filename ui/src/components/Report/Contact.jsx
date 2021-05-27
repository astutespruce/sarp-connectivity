import React from 'react'
import PropTypes from 'prop-types'
import { Text, View } from '@react-pdf/renderer'

import { Link, Section } from './elements'
import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const Contact = ({ barrierType, sarpid }) => (
  <View style={{ backgroundColor: '#ebedee', borderRadius: 12, padding: 12 }}>
    <Section title="Contact us">
      <Text>
        If you see an issue with the details for this barrier, please{' '}
        <Link
          href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
            barrierType === 'dams' ? 'dam' : 'road-related barrier'
          }: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
        >
          let us know!
        </Link>
        {'\n\n'}
        If you would like more information about this barrier or the aquatic
        connectivity analysis results presented above, please{' '}
        <Link href="mailto:Kat@southeastaquatics.net">contact us</Link>.
      </Text>
    </Section>
  </View>
)

Contact.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
}

export default Contact
