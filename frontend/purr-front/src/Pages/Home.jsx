import React from 'react'
import Sidebar from '../Components/Sidebar'

function Home() {
  return (
  <div className='flex min-h-screen'>
    <Sidebar/>

    <main className='flex-1 flex mb-80 items-center justify-center p-6'>
      <h1 className='text-5xl text-gray-400 font-bold'>purrplexity</h1>
    </main>
  </div>
  )
}

export default Home