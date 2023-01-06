import React from 'react'
import PropTypes from 'prop-types'

import { BarrierReport } from 'views'

import { ClientOnly, SEO } from 'components/Layout'

const BarriersReportRoute = ({ params: { sarpid } }) => (
  <ClientOnly>
    <BarrierReport barrierType="small_barriers" sarpid={sarpid} />
  </ClientOnly>
)

BarriersReportRoute.propTypes = {
  params: PropTypes.shape({ sarpid: PropTypes.string.isRequired }).isRequired,
}

export default BarriersReportRoute

export const Head = () => <SEO title="Download a Report" />
