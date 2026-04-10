import React from 'react'
import {
    CCard,
    CCardBody,
    CCardHeader,
    CCol,
    CContainer,
    CRow,
} from '@coreui/react'


const Chat = () => {
    return (
        <CContainer>
            <h1>Chat with LLM</h1>
            <CRow className="mb-4">
        <CCol className="mb-4">
            <div>
                <CCard className="mb-4">
                    <CCardHeader>
                        Chat with LLM here
                    </CCardHeader>
                    <CCardBody>
                        This is where the chat interface will be implemented.
                    </CCardBody>
                </CCard>
            </div>
        </CCol>
        <CCol className="mb-4">
            <CCard className="mb-4">
                <CCardHeader>
                    RAG Editor
                </CCardHeader>
                <CCardBody>
                    This is where the RAG editor will be implemented.
                </CCardBody>
            </CCard>
        </CCol>
        </CRow>
        </CContainer>
    )
}

export default Chat