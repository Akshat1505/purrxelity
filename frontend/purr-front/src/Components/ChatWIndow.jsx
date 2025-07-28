import React from 'react'

function ChatWIndow() {
  return (
    <div className='flex flex-col flex-1 p-6 justify-center items-center text-gray-300'>
      <div className='relative flex justify-center items-center gap-4 mb-4 text-5xl font-bold'>
        <span style={{fontFamily:'GruvBox'}} className=' text-[#ebdbb2]'>purrxelity</span>
        <img src="logo1.svg" className='w-13 invert abosulte left-1/2-translate-x-[105%]' alt="" />
        
      </div>
      <input style={{fontFamily:'GruvBox'}}
        type='text'
        placeholder='Lets Go... Start Purring'
        className='w-3/4 h-12 py-2 pl-4 rounded-md text-white placeholder-gray-400 border border-white/20 bg-[#404040] focus:outline-none mt-3'/>      
    </div>
  )
}

export default ChatWIndow