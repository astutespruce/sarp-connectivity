import React from 'react'

import DownloadForm from 'components/DownloadForm'
import Modal from 'components/Modal'

import Layout from 'components/Layout'

const FormPage = () => (
  <Layout>
    <Modal title="Download prioritized barriers">
      <DownloadForm />
    </Modal>
  </Layout>
)

FormPage.propTypes = {}

export default FormPage
