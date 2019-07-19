import React from 'react'

import Layout from 'components/Layout'
import {Provider as CrossfilterProvider} from 'components/Crossfilter'
import { PrioritizeWorkflow } from 'components/Priority'
import {BarrierTypeProvider} from 'components/Data'

import { FILTERS } from '../../../config/filters'

const dams = () => {
  return (
    <Layout title="Prioritize dams">
      <BarrierTypeProvider barrierType='dams'>
        <CrossfilterProvider filterConfig={FILTERS.dams}>
        <PrioritizeWorkflow />
      </CrossfilterProvider>
      </BarrierTypeProvider>
    </Layout>
  )
}

export default dams
