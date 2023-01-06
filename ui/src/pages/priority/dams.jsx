import React from 'react'

import { Layout, ClientOnly, SEO } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { dams } from 'filters'

const PrioritizeDamsPage = () => (
  <Layout>
    <ClientOnly>
      <BarrierTypeProvider barrierType="dams">
        <CrossfilterProvider filterConfig={dams}>
          <PrioritizeWorkflow />
        </CrossfilterProvider>
      </BarrierTypeProvider>
    </ClientOnly>
  </Layout>
)

export default PrioritizeDamsPage

export const Head = () => <SEO title="Prioritize dams" />
