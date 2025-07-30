import React from 'react'
import { useRef } from 'react';
import { useState } from 'react';
import { ArrowRight } from 'lucide-react';

function ChatWIndow() {
  const [active,setActive] = useState(1);
  const fileInputRef = useRef(null);

  // Handling the File Picker
  const handleAttachmentClick=()=>{
    if(fileInputRef.current){
      fileInputRef.current.click(); // opens the file exp
    }
  }

  const hadnleFileChange =(e)=>{
    const files = e.target.files;
    if(files && files.length >0){
      console.log('Files selected', files);
      
    }
  }

  return (
    <div className='flex flex-col flex-1 p-6 justify-center items-center text-gray-300'>
      <div className='relative flex justify-center items-center gap-4 mb-4 text-5xl font-bold'>
        <span style={{fontFamily:'GruvBox'}} className=' text-[#ebdbb2]'>purrxelity</span>
        
      </div>
      <div className='flex w-1/2 mt-3'>
          <input style={{fontFamily:'GruvBox'}}
            type='text'
            placeholder='Lets Go... Start Purring'
            className='flex-1 w-1/2 h-12 py-2 pl-4 rounded-md text-white placeholder-gray-400 border border-white/20 bg-[#404040] focus:outline-none mt-3'/>  
            <button className='cursor-pointer h-12 px-4 border-white/20 border-1-0 flex items-center justify-center rounded-md mt-3  ml-3 rouneded-r-mg bg-[#ebdbb2] border '>
            <ArrowRight className='invert' />
              </button> 
             <button onClick={handleAttachmentClick} className={`ml-3 h-12 mt-3 p-3 cursor-pointer rounded-lg transition-all duration-200 border border-[#ebdbb2]`}>
               <img className='w-6 invert-75' src="attach.svg" alt="" />
             </button>
             {/* Hidden */}
             <input type="file" ref={fileInputRef} style={{display:'none'}} multiple onChange={hadnleFileChange} />
        </div>   
      <div className='flex bg-[#1a1a1a] rounded-xl p-2 mr-130 scale-71  gap-2'>
        <button onClick={()=>setActive(1)} className={`p-3 w-20l cursor-pointer rounded-lg transition-all duration-200 ${active === 1 ? 'bg-[#ebdbb2]/20 border border-[#ebdbb2]': ' opacity-60'}`}>
          <img className='w-6 ml-1 invert-75' src="seach1.svg" alt="" />
        </button>
        <button onClick={()=>setActive(0)} className={`p-3 w-20 l cursor-pointer rounded-lg transition-all duration-200 ${active === 0 ? 'bg-[#ebdbb2]/20 border border-[#ebdbb2]': ' opacity-60'}`}>
          <img className='w-6 ml-3.5 invert-75' src="brain.svg" alt="" />
        </button>
      </div>
    </div>
  )
}

export default ChatWIndow