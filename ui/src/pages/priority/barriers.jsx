import React from 'react'

import Layout from 'components/Layout'
import { PrioritizeWorkflow } from 'components/Priority'
import { BarrierTypeProvider } from 'components/Data'

const PrioritizeBarriersPage = () => {
  return (
    <Layout title="Prioritize road-related barriers">
      <BarrierTypeProvider barrierType="barriers">
        <PrioritizeWorkflow />
      </BarrierTypeProvider>
    </Layout>
  )
}

export default PrioritizeBarriersPage
