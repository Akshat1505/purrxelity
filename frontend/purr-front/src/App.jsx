import { useState } from 'react'
import { BrowserRouter,Routes,Route } from 'react-router-dom'
import React from 'react'
import Home from './Pages/Home'
import './App.css'
import Login from './Pages/Login'
import SignUp from './Pages/SignUp'

function App() {
  const [count, setCount] = useState(0)

  return (
  <BrowserRouter>
    <Routes>
      <Route path='/' element={<Home/>}/>
      <Route path='/login' element={<Login/>}/>
      <Route path='/signup' element={<SignUp/>}></Route>
    </Routes>
  </BrowserRouter>
  )
}

export default App
