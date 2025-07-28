import React from 'react'
import { useNavigate } from 'react-router-dom'

function Sidebar() {
  const navigate = useNavigate();

  return (
    <div style={{fontFamily:'GruvBox'}} className='w-30  text-white h-screen bg-[#665c54] p-4 flex flex-col justify-between '>
      <img src="logo1.svg" alt="" className='w-18 invert' />
      <button className='mt-6 flex items-center space-x-2 text-white text-sm hover:text-gray-300'>
        <div className='ml-4 mt-10 w-10 h-10 border border-white rounded-lg flex items-center justify-center'>
          <img className=' w-10 invert cursor-pointer ' src="plus-svgrepo-com.svg" alt="" />
        </div>
      </button>
      <ul style={{fontFamily:'GruvBox'}} className='space-y-2 mt-10'>
        <li  className='text-lg '>History</li>
      </ul>
      <button onClick={()=>navigate('/login')} className='flex-col cursor-pointer mb-4 flex items-center '>
        <img className='mt-110 invert w-15 ' src="user.svg" alt="" />
        <span className=' text-white text-lg'>Account</span>
      </button>
    </div>
  )
}

export default Sidebar