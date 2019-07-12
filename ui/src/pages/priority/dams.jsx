import React from 'react'

import Layout from 'components/Layout'
import { PrioritizeWorkflow } from 'components/Priority'

const dams = () => {
  return (
    <Layout title="Prioritize dams">
      <PrioritizeWorkflow barrierType="dams" />
    </Layout>
  )
}

export default dams
