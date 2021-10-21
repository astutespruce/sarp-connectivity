import React from 'react'
import PropTypes from 'prop-types'

import { useQuery } from 'react-query'

import NotFound from 'pages/404'
import { fetchBarrierDetails } from 'components/Data/API'
import { Preview } from 'components/ReportPreview'

import { Layout, PageError, PageLoading } from 'components/Layout'

const BarrierReport = ({ barrierType, sarpid, uri }) => {
  const { isLoading, error, data } = useQuery(
    uri,
    async () => fetchBarrierDetails(barrierType, sarpid),
    {
      // FIXME:
      //   staleTime: 60 * 60 * 1000, // 60 minutes
      staleTime: 1, // use then reload to force refresh of underlying data during dev
      refetchOnWindowFocus: false,
      refetchOnMount: false,
    }
  )

  if (isLoading) {
    return (
      <Layout title="Loading...">
        <PageLoading />
      </Layout>
    )
  }

  if (error) {
    console.error(`Error loading dam with SARPID: ${sarpid}`)

    return (
      <Layout title={`Error loading dam ${sarpid}`}>
        <PageError />
      </Layout>
    )
  }

  if (!data) {
    return <NotFound />
  }

  const { name } = data

  return (
    <Layout title={name}>
      <Preview barrierType={barrierType} data={data} />
    </Layout>
  )
}

BarrierReport.propTypes = {}

// Since these come from the router, they may be undefined during prop validation
BarrierReport.propTypes = {
  barrierType: PropTypes.string,
  sarpid: PropTypes.string,
  uri: PropTypes.string,
}

BarrierReport.defaultProps = {
  barrierType: null,
  sarpid: null,
  uri: null,
}

export default BarrierReport