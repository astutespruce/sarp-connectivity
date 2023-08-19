import React from 'react'

import { Layout, ClientOnly, SEO } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { combinedBarriers } from 'filters'

const PrioritizeLargefishBarriersPage = () => (
  <Layout>
    <ClientOnly>
      <BarrierTypeProvider barrierType="largefish_barriers">
        <CrossfilterProvider filterConfig={combinedBarriers}>
          <PrioritizeWorkflow />
        </CrossfilterProvider>
      </BarrierTypeProvider>
    </ClientOnly>
  </Layout>
)

export default PrioritizeLargefishBarriersPage

export const Head = () => (
  <SEO title="Prioritize dams & road-related barriers for large-bodied fish" />
)
