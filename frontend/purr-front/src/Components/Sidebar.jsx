import React from 'react'

function Sidebar() {
  return (
    <div className='w-30 text-white h-screen bg-[#090909] p-4 ml-6'>
      <img src="logo1.svg" alt="" className='w-18 invert' />
      <ul className='space-y-2 mt-10'>
        <li className='text-xs'>Home</li>
        <li className='text-xs'>Discover</li>
        <li className='text-xs'>Login/SignUp</li>
      </ul>
    </div>
  )
}

export default Sidebar