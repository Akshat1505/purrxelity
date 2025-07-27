import React from 'react'

function Sidebar() {
  return (
    <div className='w-64 text-white h-screen bg-purple-400 rounded-lg p-4'>
      <h2 className='text-xl font-semibold mb-4'>Sidebar</h2>
      <ul className='space-y-2'>
        <li>Home</li>
        <li>Discover</li>
        <li>Login/SignUp</li>
      </ul>
    </div>
  )
}

export default Sidebar