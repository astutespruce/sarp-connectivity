import React, { useState, memo } from 'react'
import { navigate } from 'gatsby'
import { Trash } from '@emotion-icons/fa-solid'
import { Button } from 'theme-ui'

import Confirm from 'components/Confirm'

const StartOverButton = () => {
  const [confirmIsActive, setConfirmIsActive] = useState(false)

  const handleConfirm = () => {
    setConfirmIsActive(false)
    navigate('/priority')
  }

  const handleClick = () => {
    setConfirmIsActive(true)
  }

  return (
    <>
      {confirmIsActive && (
        <Confirm
          title="Start Over?"
          onConfirm={handleConfirm}
          onClose={() => setConfirmIsActive(false)}
        >
          You will lose all your work. Are you sure?
        </Confirm>
      )}

      <Button
        variant="warning"
        title="Start Over"
        onClick={handleClick}
        sx={{ mr: '1rem', fontSize: '1.1em' }}
      >
        <Trash size="1em" />
      </Button>
    </>
  )
}

export default memo(StartOverButton)
