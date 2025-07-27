import React from 'react'

function Sidebar() {
  return (
    <div className='w-30 text-white h-screen bg-[#404040] p-4'>
      <h2 className='text-xl font-semibold mb-4'>Sidebar</h2>
      <ul className='space-y-2'>
        <li className='text-xs'>Home</li>
        <li className='text-xs'>Discover</li>
        <li className='text-xs'>Login/SignUp</li>
      </ul>
    </div>
  )
}

export default Sidebar