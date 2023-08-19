import React from 'react'

import { Layout, ClientOnly, SEO } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { combinedBarriers } from 'filters'

const PrioritizeSmallfishBarriersPage = () => (
  <Layout>
    <ClientOnly>
      <BarrierTypeProvider barrierType="smallfish_barriers">
        <CrossfilterProvider filterConfig={combinedBarriers}>
          <PrioritizeWorkflow />
        </CrossfilterProvider>
      </BarrierTypeProvider>
    </ClientOnly>
  </Layout>
)

export default PrioritizeSmallfishBarriersPage

export const Head = () => (
  <SEO title="Prioritize dams & road-related barriers for small-bodied fish" />
)
