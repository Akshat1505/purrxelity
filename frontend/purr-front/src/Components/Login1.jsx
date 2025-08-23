import { useState } from "react"
import { useNavigate } from "react-router-dom"

const Login1 = () => {
  const navigate = useNavigate();

  return (
    <div className='h-screen flex flex-col items-center justify-center bg-black'>
      <button onClick={()=> navigate('/')}  style={{fontFamily:'GruvBox'}} className='cursor-pointer text-white absolute top-5 left-5 text-2xl'>purrXelity</button>
      <h1 className='text-white -translate-y-35 flex   text-3xl'>Welcome back</h1>
      <div className='bg-gray-200 items-center justify-center w-95 p-2 -translate-y-25 rounded-lg shadow-lg'>
        <input type="email" placeholder='Email' className='w-full rounded text-black focus:outline-none  ' />
      </div>
      <div className='bg-gray-200 mt-5 items-center justify-center w-95 p-2 -translate-y-25 rounded-lg shadow-lg'>
        <input type="password" placeholder='Password' className='w-full rounded text-black focus:outline-none  ' />
      </div>
      <span onClick={()=>navigate('/signup')} className=" cursor-pointer hover:text-blue-200 text-white -translate-y-22 -translate-x-37 ">New User?</span>
      
      <button  style={{fontFamily:'GruvBox'}} className='bg-gray-100 flex -translate-y-18 items-center justify-center cursor-pointer hover:bg-amber-100  rounded-lg w-24 h-10 '>Login</button>
      
    </div>
  )
}

export default Login1