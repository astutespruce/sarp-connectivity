import React from 'react'

import Layout, { ClientOnly } from 'components/Layout'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'
import { FILTERS } from '../../../config/filters'

const dams = () => (
  <Layout title="Prioritize dams">
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
