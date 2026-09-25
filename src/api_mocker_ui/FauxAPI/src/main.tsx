import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import HomeView from './Home.tsx'
import RegistrationView from './registration.tsx'


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <>
      <BrowserRouter>
      <Routes>
        <Route index element={<App />}/>
        <Route path='/home' element={<HomeView/>} />
        <Route path='/registration' element={<RegistrationView/>} />
      </Routes>
      </BrowserRouter>
   </>

  </StrictMode>,
)
