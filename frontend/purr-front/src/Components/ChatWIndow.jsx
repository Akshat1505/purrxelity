import React from 'react'
import { useRef } from 'react';
import { useState } from 'react';
import { ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { Navigate, useNavigate } from 'react-router-dom';


function ChatWIndow() {
  const [active,setActive] = useState(1);
  const [inputText, setInputText] = useState('');
  const [response,setResponse] = useState('');
  const fileInputRef = useRef(null);
  const [isChatStarted, setIsChatStarted] = useState(false);
  const [message,setMessage] = useState([]);
  const [isTyping , setIsTyping ] = useState(false);
  const navigate = useNavigate();

  // handle ssending msg to backend
  const handleSend = async ()=>{
    if(!inputText.trim()) return;

    setMessage(prev=>[...prev, {sender:'user', text: inputText}])
    setInputText('');
    const formData = new FormData();
    formData.append('input', inputText);

    try{
      const res = await fetch('http://localhost:8000/chat',{
        method: 'POST',
        headers: {'Content-Type' : 'application/json'},
        body: JSON.stringify({input:inputText}),
      })
      if(!res.ok){
        throw new Error(`Server responded with Status ${res.status}`)
      }
      const data = await res.json();
      const typeText = (text)=>{
        let index = 0;  
        setMessage(prev=>[...prev,{sender:'ai' , text: ''}])

        const interval = setInterval(() => {
            index++;
            setMessage(prev=>{
              const newMesg = [...prev];
              newMesg[newMesg.length-1].text= text.slice(0,index);
              return newMesg;
            });
            if(index >= text.length){
              clearInterval(interval);
              setIsTyping(false);
            }
        }, 20);
      }
      console.log('Reply:', data.message);
      setResponse(data.message);
      setIsChatStarted(true);
      const cleanData = data.message.replace(/^"(.*)"$/, '$1').replace(/\n/g, ' ').replace(/\*/g, '').replace(/\s+/g, ' ').replace(/\\n/g, ' ').trim();
      typeText(cleanData);
    }catch (error){
      setResponse('Well There is Problem..');
      console.error('Error Sending message', error);
    }
  }

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
    <div className='flex flex-col flex-1 p-6 justify-center items-center text-gray-300 rel'>
      <div className='relative flex justify-center items-center gap-4 mb-4 text-5xl font-bold'>
      </div>
      <div className='relative w-full h-full'>
        <button onClick={()=>navigate('/login')} style={{fontFamily:'GruvBox'}} className='fixed top-4 right-10 cursor-pointer rounded-md transition hover:bg-blue-600  px-3 py-2 bg-gray-400 text-black ' >
            Login/SignUp
        </button>
      </div>
      <div className='flex flex-col w-full max-w-2xl mb-4 space-y-2'>
        {message.map((msg,idx)=>(
          <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div  className={`px-4 py-2 rounded-md ${msg.sender === 'user' ? 'bg-[#212121] text-white' : 'bg-black text-gray-100'}`} style={msg.sender !== 'user' ? {fontFamily:'GruvBox'}:{}}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>
      {/* Input Bar */}
      <motion.div className=' flex w-1/2 mt-3' initial={{y: 0}} animate={isChatStarted ? {y: 50}: {y:0}} transition={{ease:'easeInOut', duration:0.5}}>
        <div className='flex items-center bg-[#404040] rounded-md px-2 py-1 w-full' style={{fontFamily:'GruvBox'}}>
          <input
            type='text'
            placeholder='Lets Go... Start Purring'
            className='flex-1 h-12 py-2 pl-4 rounded-md text-white placeholder-gray-400 bg-transparent focus:outline-none'
            value={inputText}
            onChange={(e)=>setInputText(e.target.value)}
          />
          <button onClick={handleAttachmentClick} className='p-2 rounded hover:bg-[#505050] transition ml-2 cursor-pointer'>
            <img className='w-6 invert-75' src="attach.svg" alt="" />
          </button>
          <button onClick={handleSend} className='p-2 rounded hover:bg-[#505050] transition ml-2 cursor-pointer flex items-center justify-center'>
            <ArrowRight className='invert' />
          </button>
          {/* Hidden */}
          <input type="file" ref={fileInputRef} style={{display:'none'}} multiple onChange={hadnleFileChange} />
        </div>
      </motion.div>
      {/* <div className='flex bg-[#1a1a1a] rounded-xl p-2 mr-130 scale-71  gap-2'>
        <button onClick={()=>setActive(1)} className={`p-3 w-20l cursor-pointer rounded-lg transition-all duration-200 ${active === 1 ? 'bg-[#ebdbb2]/20 border border-[#ebdbb2]': ' opacity-60'}`}>
          <img className='w-6 ml-1 invert-75' src="seach1.svg" alt="" />
        </button>
        <button onClick={()=>setActive(0)} className={`p-3 w-20 l cursor-pointer rounded-lg transition-all duration-200 ${active === 0 ? 'bg-[#ebdbb2]/20 border border-[#ebdbb2]': ' opacity-60'}`}>
          <img className='w-6 ml-3.5 invert-75' src="brain.svg" alt="" />
        </button>
      </div> */}
    </div>
  )
}

export default ChatWIndow