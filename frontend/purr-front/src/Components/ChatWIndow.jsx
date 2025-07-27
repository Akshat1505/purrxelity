import React from 'react'

function ChatWIndow() {
  return (
    <div className='flex flex-col flex-1 p-6 justify-center items-center text-gray-300'>
      <div className='text-5xl mb-4 font-bold'>purrxelity</div>
      <div className='text-center text-gray-400 mb-4 text-2xl font-medium'>
        Start Typing
      </div>
      <input
        type='text'
        placeholder='Ask Anything..'
        className='w-3/4 py-2 rounded-md text-white placeholder-gray-400 bg-[#404040] focus:outline-none'/>      
    </div>
  )
}

export default ChatWIndow