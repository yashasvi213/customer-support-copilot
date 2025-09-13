import React from 'react'
import ReactDOM from 'react-dom/client'
import CustomerSupportUI from './SupportUI.jsx'
import { Analytics } from '@vercel/analytics/react'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <CustomerSupportUI />
    <Analytics />
  </React.StrictMode>,
)
