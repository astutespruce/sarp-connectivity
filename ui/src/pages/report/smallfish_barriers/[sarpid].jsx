import React from 'react'
import PropTypes from 'prop-types'

import { BarrierReport } from 'views'

import { ClientOnly, SEO } from 'components/Layout'

const SmallfishBarriersReportRoute = ({ params: { sarpid } }) => (
  <ClientOnly>
    <BarrierReport networkType="smallfish_barriers" sarpid={sarpid} />
  </ClientOnly>
)

SmallfishBarriersReportRoute.propTypes = {
  params: PropTypes.shape({ sarpid: PropTypes.string.isRequired }).isRequired,
}

export default SmallfishBarriersReportRoute

export const Head = () => <SEO title="Download a Report" />
