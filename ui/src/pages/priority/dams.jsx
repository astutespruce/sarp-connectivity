import React from 'react'

import Layout from 'components/Layout'
import { PrioritizeWorkflow } from 'components/Priority'
import {BarrierTypeProvider} from 'components/Data'

const dams = () => {
  return (
    <Layout title="Prioritize dams">
      <BarrierTypeProvider barrierType='dams'>
      <PrioritizeWorkflow />
      </BarrierTypeProvider>
    </Layout>
  )
}

export default dams
