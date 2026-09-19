import { useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import {Navigate, useNavigate}  from "react-router-dom"
import './App.css'

function App() {
  
  const [count, setCount] = useState(0)
  const nav = useNavigate()
  let starter = ()=>{
    nav("/home")
  }
  return (
    <section style={{ "height":"100vh","width":"100vw","display":"flex","justifyContent":"center","alignItems":"center","flexFlow":"column"}} className="">

        <h1>Welcome To Faux API</h1>  
        <button style={{"padding":"15px 30px","background":"#692327","color":"#a59396","fontWeight":"bolder","fontSize":"18pt","border":"none","borderRadius":"5px"}} onClick={starter}>
          get started</button>
    </section>
  )
}

export default App
