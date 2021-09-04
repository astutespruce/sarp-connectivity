import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Flex } from 'theme-ui'

import TabBar from './TabBar'
import TabContainer from './TabContainer'

const Tabs = ({ children, sx }) => {
  const tabs = children.map(({ props: { id, label } }) => ({ id, label }))
  const firstTab = tabs[0].id

  const [tab, setTab] = useState(firstTab)

  // if active tab is no longer one of children, reset to first tab
  useEffect(() => {
    if (
      children.map(({ props: { id } }) => id).filter((id) => id === tab)
        .length === 0
    ) {
      setTab(firstTab)
    }
  }, [children, firstTab, tab])

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
