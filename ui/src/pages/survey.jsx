import React from 'react'

import { BarrierTypeProvider } from 'components/Data'
import { Provider as CrossfilterProvider } from 'components/Crossfilter'
import { Layout, ClientOnly, SEO } from 'components/Layout'
import { SurveyWorkflow } from 'components/Survey'
import { roadCrossings } from 'filters'

const SurveyRoadCrossingsPage = () => (
  <Layout>
    <ClientOnly>
      <BarrierTypeProvider barrierType="road_crossings">
        <CrossfilterProvider filterConfig={roadCrossings}>
          <SurveyWorkflow />
        </CrossfilterProvider>
      </BarrierTypeProvider>
    </ClientOnly>
  </Layout>
)

export default SurveyRoadCrossingsPage

export const Head = () => <SEO title="Select road crossings to survey" />
