import React from 'react'
import Sidebar from '../Components/Sidebar'
import ChatWindow from '../Components/ChatWIndow'
import Login from '../Components/Login1'

function Home() {
  return (
  <div className='flex min-h-screen'>
    <Sidebar/>

    <main className='flex-1 flex mb-80 items-center justify-center p-6'>
      <ChatWindow/>
    </main>
  </div>
  )
}

export default Home