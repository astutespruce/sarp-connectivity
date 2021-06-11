import React from 'react'
import { Router } from '@reach/router'

import { ClientOnly } from 'components/Layout'
import { DamReport, BarrierReport } from 'views/report'
import NotFound from 'pages/404'

const DynamicRouter = () => (
  <ClientOnly>
    <Router style={{ height: '100%' }}>
      <DamReport path="/report/dams/:sarpid/*" />
      <BarrierReport path="/report/barriers/:sarpid/*" />
      <NotFound default />
    </Router>
  </ClientOnly>
)

export default DynamicRouter
