import React from 'react'
import { CFooter } from '@coreui/react'

const AppFooter = () => {
  return (
    <CFooter className="px-4">
      <div>
        <a href="#"> Top of the Page</a>
      </div>
    </CFooter>
  )
}

export default React.memo(AppFooter)
