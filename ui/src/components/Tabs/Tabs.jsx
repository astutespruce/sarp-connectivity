import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Flex } from 'theme-ui'

import TabBar from './TabBar'
import TabContainer from './TabContainer'

const Tabs = ({ children, sx }) => {
  const tabs = children.map(({ props: { id, label } }) => ({ id, label }))
  const firstTab = tabs[0].id

  const [tab, setTab] = useState(firstTab)

  const handleTabChange = (id) => {
    setTab(id)
  }

  return (
    <Flex sx={{ flexDirection: 'column', ...sx }}>
      <TabBar tabs={tabs} activeTab={tab} onChange={handleTabChange} />
      <TabContainer activeTab={tab}>{children}</TabContainer>
    </Flex>
  )
}

Tabs.propTypes = {
  children: PropTypes.arrayOf(PropTypes.node).isRequired,
  sx: PropTypes.object,
}

Tabs.defaultProps = {
  sx: {},
}

export default Tabs
