import React from 'react'

import { Layout, ClientOnly } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { FILTERS } from '../../../config/filters'

const PrioritizeBarriersPage = () => (
  <Layout title="Prioritize road-related barriers">
    <ClientOnly>
      <BarrierTypeProvider barrierType="small_barriers">
        <CrossfilterProvider filterConfig={FILTERS.smallBarriers}>
          <PrioritizeWorkflow />
        </CrossfilterProvider>
      </BarrierTypeProvider>
    </ClientOnly>
  </Layout>
)

export default PrioritizeBarriersPage
