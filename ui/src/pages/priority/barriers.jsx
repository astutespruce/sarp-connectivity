import React from 'react'

import { Layout, ClientOnly, SEO } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { FILTERS } from 'config/filters'

const PrioritizeBarriersPage = () => (
  <Layout>
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

export const Head = () => <SEO title="Prioritize road-related barriers" />
