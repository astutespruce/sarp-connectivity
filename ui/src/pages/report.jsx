import React from 'react'
import { Router } from '@reach/router'

import { ClientOnly } from 'components/Layout'
import { BarrierReport } from 'views'
import NotFound from 'pages/404'

const DynamicRouter = () => (
  <ClientOnly>
    <Router style={{ height: '100%' }}>
      <BarrierReport path="/report/:barrierType/:sarpid" />
      <NotFound default />
    </Router>
  </ClientOnly>
)

export default DynamicRouter
