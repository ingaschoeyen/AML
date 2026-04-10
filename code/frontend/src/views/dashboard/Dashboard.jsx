import React from 'react'
import classNames from 'classnames'

import { 
    CAccordion, 
    CAccordionBody, 
    CAccordionHeader, 
    CAccordionItem 
} from '@coreui/react'


import {
  CAvatar,
  CButton,
  CButtonGroup,
  CCard,
  CCardBody,
  CCardFooter,
  CCardHeader,
  CCol,
  CProgress,
  CRow,
  CTable,
  CTableBody,
  CTableDataCell,
  CTableHead,
  CTableHeaderCell,
  CTableRow,
} from '@coreui/react'
import CIcon from '@coreui/icons-react'
import {
  cibCcAmex,
  cibCcApplePay,
  cibCcMastercard,
  cibCcPaypal,
  cibCcStripe,
  cibCcVisa,
  cibGoogle,
  cibFacebook,
  cibLinkedin,
  cifBr,
  cifEs,
  cifFr,
  cifIn,
  cifPl,
  cifUs,
  cibTwitter,
  cilCloudDownload,
  cilPeople,
  cilUser,
  cilUserFemale,
} from '@coreui/icons'


import WidgetsBrand from '../widgets/WidgetsBrand'
import WidgetsDropdown from '../widgets/WidgetsDropdown'

const SearchBar = () => {
  return (
    <CRow className="mb-3">
      <CCol xs={10}>
        <input type="text" className="form-control" placeholder="Enter your query here..." />
      </CCol>
      <CCol xs={2}>
        <CButton color="primary" className="w-100">Search</CButton>
      </CCol>
    </CRow>
  )
}

const SearchResults = () => {
  return (
    <CAccordion activeItemKey={2}>
      <CAccordionItem itemKey={1}>
        <CAccordionHeader>Most Relevant Results</CAccordionHeader>
        <CAccordionBody>
          Here, results that are ranked high by the vector search will be displayed. 
          These results are the most relevant to the user's query based on the semantic similarity search. 
        </CAccordionBody>
      </CAccordionItem>
      <CAccordionItem itemKey={2}>
        <CAccordionHeader>Images</CAccordionHeader>
        <CAccordionBody>
          <CRow><CCol>Image 1</CCol><CCol>Image 2</CCol></CRow>
        </CAccordionBody>
      </CAccordionItem>
      <CAccordionItem itemKey={3}>
        <CAccordionHeader>Related Results</CAccordionHeader>
        <CAccordionBody>
          Here, results that are not ranked high by the vector search but are strongly related 
          according to the graph representation will be displayed.
        </CAccordionBody>
      </CAccordionItem>
    </CAccordion>
  )
}



const Dashboard = () => {


  return (
    <>
        <SearchBar />
        <SearchResults />
    </>
  )
}

export default Dashboard
