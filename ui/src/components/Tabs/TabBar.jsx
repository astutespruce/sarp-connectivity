import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Button, Flex } from 'theme-ui'

const TabBar = ({ tabs, activeTab, onChange }) => {
  const handleClick = (id) => {
    if (id !== activeTab) {
      onChange(id)
    }
  }
  return (
    <Flex
      sx={{
        alignItems: 'center',
        justifyContent: 'space-between',
        fontSize: '0.9rem',
        flex: '0 0 auto',
        bg: 'grey.1',
      }}
    >
      {tabs.map((tab) => (
        <Button
          key={tab.id}
          variant={activeTab === tab.id ? 'tab-active' : 'tab-inactive'}
          onClick={handleClick}
          {...tab}
        />
      ))}
    </Flex>
  )
}

TabBar.propTypes = {
  tabs: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    })
  ).isRequired,
  activeTab: PropTypes.string.isRequired,
  onChange: PropTypes.func,
}

TabBar.defaultProps = {
  onChange: () => {},
}

export default memo(
  TabBar,
  (
    { tabs: prevTabs, activeTab: prevTab },
    { tabs: nextTabs, activeTab: nextTab }
  ) => prevTabs === nextTabs && prevTab === nextTab
)
