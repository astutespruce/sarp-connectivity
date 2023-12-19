import React, { memo } from 'react'
import PropTypes from 'prop-types'
import { Button, Flex } from 'theme-ui'

const tabCSS = {
  fontSize: '1rem',
  cursor: 'pointer',
  textAlign: 'center',
  flex: '1 1 auto',
  p: '0.5rem',
  color: 'grey.7',
  bg: 'blue.1',
  border: 'none',
  borderRadius: 0,
  '&:hover': {
    bg: 'blue.2',
  },
}

const activeTabCSS = {
  ...tabCSS,
  color: 'text',
  fontWeight: 'bold',
  bg: '#FFF',
  border: 'none',
  '&:hover': {
    bg: '#FFF',
  },
}

const TabBar = ({ tabs, activeTab, onChange }) => {
  const handleClick = (id) => () => {
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
          sx={activeTab === tab.id ? activeTabCSS : tabCSS}
          data={activeTab === tab.id ? 'is-active' : null}
          onClick={handleClick(tab.id)}
          {...tab}
        >
          {tab.label}
        </Button>
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
