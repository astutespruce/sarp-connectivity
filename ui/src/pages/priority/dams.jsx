import React from 'react'

import { Layout, ClientOnly, SEO } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { FILTERS } from 'config/filters'

const dams = () => (
  <Layout>
    <ClientOnly>
      <BarrierTypeProvider barrierType="dams">
        <CrossfilterProvider filterConfig={FILTERS.dams}>
          <PrioritizeWorkflow />
        </CrossfilterProvider>
      </BarrierTypeProvider>
    </ClientOnly>
  </Layout>
)

export default dams

export const Head = () => <SEO title="Prioritize dams" />
