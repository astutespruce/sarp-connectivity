import React from 'react'
import PropTypes from 'prop-types'

import { BarrierReport } from 'views'

import { ClientOnly, SEO } from 'components/Layout'

const CombinedBarriersReportRoute = ({ params: { sarpid } }) => (
  <ClientOnly>
    <BarrierReport networkType="combined_barriers" sarpid={sarpid} />
  </ClientOnly>
)

CombinedBarriersReportRoute.propTypes = {
  params: PropTypes.shape({ sarpid: PropTypes.string.isRequired }).isRequired,
}

export default CombinedBarriersReportRoute

export const Head = () => <SEO title="Download a Report" />
