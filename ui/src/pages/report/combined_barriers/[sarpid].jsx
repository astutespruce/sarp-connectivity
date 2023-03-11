import React from 'react'
import PropTypes from 'prop-types'

import { BarrierReport } from 'views'

import { ClientOnly, SEO } from 'components/Layout'

const DamsReportRoute = ({ params: { sarpid } }) => (
  <ClientOnly>
    <BarrierReport networkType="combined_barriers" sarpid={sarpid} />
  </ClientOnly>
)

DamsReportRoute.propTypes = {
  params: PropTypes.shape({ sarpid: PropTypes.string.isRequired }).isRequired,
}

export default DamsReportRoute

export const Head = () => <SEO title="Download a Report" />
