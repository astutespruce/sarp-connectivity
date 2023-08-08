import React from 'react'
import PropTypes from 'prop-types'

import { BarrierReport } from 'views'

import { ClientOnly, SEO } from 'components/Layout'

const LargefishBarriersReportRoute = ({ params: { sarpid } }) => (
  <ClientOnly>
    <BarrierReport networkType="largefish_barriers" sarpid={sarpid} />
  </ClientOnly>
)

LargefishBarriersReportRoute.propTypes = {
  params: PropTypes.shape({ sarpid: PropTypes.string.isRequired }).isRequired,
}

export default LargefishBarriersReportRoute

export const Head = () => <SEO title="Download a Report" />
