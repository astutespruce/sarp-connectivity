import React, { memo } from 'react'
import PropTypes from 'prop-types'

import { Flex } from 'components/Grid'
import styled, { themeGet } from 'style'
import Button from './Button'

const Wrapper = styled(Flex).attrs({
  alignItem: 'center',
  justifyContent: 'space-between',
})`
  background-color: ${themeGet('colors.grey.100')};
  font-size: 0.9rem;
  flex: 0 0 auto;
`

const TabBar = ({ tabs, activeTab, onChange, ...props }) => {
  const handleClick = id => {
    if (id !== activeTab) {
      onChange(id)
    }
  }
  return (
    <Wrapper {...props}>
      {tabs.map(tab => (
        <Button
          key={tab.id}
          active={activeTab === tab.id}
          onClick={handleClick}
          {...tab}
        />
      ))}
    </Wrapper>
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
