import React from 'react'
import PropTypes from 'prop-types'

import { useQuery } from '@tanstack/react-query'

import NotFound from 'pages/404'
import { fetchBarrierDetails } from 'components/Data/API'
import { Preview } from 'components/ReportPreview'

import { Layout, PageError, PageLoading } from 'components/Layout'

const BarrierReport = ({ networkType, sarpid }) => {
  const { isLoading, error, data } = useQuery({
    queryKey: [`${networkType}:${sarpid}`],
    queryFn: async () => fetchBarrierDetails(networkType, sarpid),

    staleTime: 60 * 60 * 1000, // 60 minutes
    // staleTime: 1, // use then reload to force refresh of underlying data during dev
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  if (isLoading) {
    return (
      <Layout>
        <PageLoading />
      </Layout>
    )
  }

  if (error) {
    console.error(`Error loading barrier with SARPID: ${sarpid}`)

    return (
      <Layout>
        <PageError />
      </Layout>
    )
  }

  if (!data) {
    return <NotFound />
  }

  // console.log('data', data)

  return (
    <Layout>
      <Preview networkType={networkType} data={data} />
    </Layout>
  )
}

BarrierReport.propTypes = {}

// Since these come from the router, they may be undefined during prop validation
BarrierReport.propTypes = {
  networkType: PropTypes.string.isRequired,
  sarpid: PropTypes.string.isRequired,
}

export default BarrierReport
