import React from 'react'
import classNames from 'classnames'

import {
  CAvatar,
  CAccordion,
  CAccordionBody,
  CAccordionHeader,
  CAccordionItem,
  CButton,
  CButtonGroup,
  CCard,
  CCardBody,
  CCardFooter,
  CCardHeader,
  CCol,
  CContainer,
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

import avatar1 from 'src/assets/images/avatars/1.jpg'
import avatar2 from 'src/assets/images/avatars/2.jpg'
import avatar3 from 'src/assets/images/avatars/3.jpg'
import avatar4 from 'src/assets/images/avatars/4.jpg'
import avatar5 from 'src/assets/images/avatars/5.jpg'
import avatar6 from 'src/assets/images/avatars/6.jpg'

import WidgetsBrand from '../widgets/WidgetsBrand'
import WidgetsDropdown from '../widgets/WidgetsDropdown'
import MainChart from './MainChart'

import mapNL from 'src/assets/images/nl_map.svg'

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
    <CAccordion alwaysOpen activeItemKey={2}>
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

const MapPreview = () => {
  return (
    <div style={{ height: '300px', width: '400px', backgroundColor: '#e9ecef', paddingTop: '50px' }} className="mb-4">
      <img src={mapNL} alt="Map Preview" style={{ width: '100%', height: '100%' }} />
    </div>
  )
}

const GraphPreview = () => {
  return (
    <div style={{ height: '300px', width: '400px', backgroundColor: '#e9ecef' }} className="mb-4">
      Graph preview will be displayed here.
    </div>
  )
}

const Dashboard = () => {


  return (
    <>
      <CCard className="mb-4">
        <SearchBar />
        <SearchResults />
      </CCard>
      <CContainer>
        <CRow>
          <CCol className="mb-4">
            <MapPreview />
            <GraphPreview />
          </CCol>
          <CCol className="mb-4">
            Here, information relating to a selected asset will be displayed.
          </CCol>
          </CRow>
      </CContainer>
    </>
  )
}

export default Dashboard
