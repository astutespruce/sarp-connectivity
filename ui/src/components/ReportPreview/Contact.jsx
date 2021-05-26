import React from 'react'
import PropTypes from 'prop-types'
import { Box, Text } from 'theme-ui'

import { siteMetadata } from '../../../gatsby-config'

const { version: dataVersion } = siteMetadata

const Contact = ({ barrierType, sarpid }) => (
  <Box sx={{ bg: 'grey.1', borderRadius: '1rem', p: '1rem' }}>
    <Text sx={{ fontWeight: 'bold', fontSize: 3 }}>Contact us</Text>
    <Box sx={{ mt: '0.5rem' }}>
      <Text>
        If you see an issue with the details for this barrier, please{' '}
        <a
          href={`mailto:Kat@southeastaquatics.net?subject=Problem with SARP Inventory for ${
            barrierType === 'dams' ? 'dam' : 'road-related barrier'
          }: ${sarpid} (data version: ${dataVersion})&body=I found the following problem with the SARP Inventory for this barrier:`}
        >
          let us know!
        </a>
        <br />
        <br />
        If you would like more information about this barrier or the aquatic
        connectivity analysis results presented above, please{' '}
        <a href="mailto:Kat@southeastaquatics.net">contact us</a>.
      </Text>
    </Box>
  </Box>
)

Contact.propTypes = {
  barrierType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
}

export default Contact
