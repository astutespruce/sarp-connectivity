import React from 'react'

import { Layout, ClientOnly, SEO } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { combinedBarriers } from 'filters'

const PrioritizeCombinedBarriersPage = () => (
  <Layout>
    <ClientOnly>
      <BarrierTypeProvider barrierType="combined_barriers">
        <CrossfilterProvider filterConfig={combinedBarriers}>
          <PrioritizeWorkflow />
        </CrossfilterProvider>
      </BarrierTypeProvider>
    </ClientOnly>
  </Layout>
)

export default PrioritizeCombinedBarriersPage

export const Head = () => (
  <SEO title="Prioritize dams & road-related barriers" />
)
