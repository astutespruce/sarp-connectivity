import React from 'react'

import Layout from 'components/Layout'
import { PrioritizeWorkflow } from 'components/Priority'

const PrioritizeBarriersPage = () => {
  return (
    <Layout title="Prioritize road-related barriers">
      <PrioritizeWorkflow barrierType="barriers" />
    </Layout>
  )
}

export default PrioritizeBarriersPage
