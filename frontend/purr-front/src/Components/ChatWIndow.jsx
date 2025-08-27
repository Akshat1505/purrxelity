import React, { useEffect } from 'react'
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
  const [threadId , setThreadId] = useState(null);
  const [greet , setGreet] = useState('');
  const navigate = useNavigate();

  useEffect(()=>{
    const hour = new Date().getHours();
    if(hour >= 5 && hour <12) setGreet('Good Morning');
    else if(hour >= 12 && hour < 18) setGreet('Good Afternoon');
    else setGreet('Good Evening');
  },[])

  const ensureThread = async () => {
    if(threadId) return threadId;
    const res = await fetch("http://localhost:8000/users/1/chats",{
      method: "POST",
      headers: {"Content-Type" : "application/json"},
      body: JSON.stringify({thread_id: null,
        messages: []
      }),
    });
    const data = await res.json();
    setThreadId(data.thread_id);
    return data.thread_id;
  }
  // handle ssending msg to backend
  const handleSend = async ()=>{
    if(!inputText.trim()) return;

    setMessage(prev=>[...prev, {sender:'user', text: inputText}])
    setInputText('');
    const currentThread = await ensureThread();

    try{
      const res = await fetch('http://localhost:8000/chat?user_id=1',{
        method: 'POST',
        headers: {'Content-Type' : 'application/json'},
        body: JSON.stringify({input:inputText,
          thread_id: currentThread,
        }),
      });
      const data = await res.json();
      console.log("reply" , data.message);
      
      if(!res.ok){
        throw new Error(`Server responded with Status ${res.status}`)
      }
      
      console.log('Reply:', data.message);
      setResponse(data.message);
      setIsChatStarted(true);
      const cleanData = data.message.replace(/^"(.*)"$/, '$1').replace(/\n/g, ' ').replace(/\*/g, '').replace(/\s+/g, ' ').replace(/\\n/g, ' ').trim();
      setMessage(prev=>[...prev,
        {sender:'ai' , text: cleanData}
      ])
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
      {greet && !isChatStarted && (
        <div style={{fontFamily:'GruvBox'}} className='mb-2 text-4xl font-semibold text-gray-300'>
          {greet}
        </div>
      )}
      <div className='relative flex justify-center items-center gap-4 mb-4 text-5xl font-bold'>
      </div>
      <div className='relative w-full h-full'>
        <button onClick={()=>navigate('/login')} style={{fontFamily:'GruvBox'}} className='fixed top-4 right-10 cursor-pointer rounded-md transition hover:bg-blue-600  px-3 py-2 bg-gray-400 text-black ' >
            Login/SignUp
        </button>
      </div>
      <div className='flex flex-col w-1/2 mx-atuo  space-y-2'>
        {message.map((msg,idx)=>(
          <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end ' : 'justify-start'}`}>
            <div  className={`px-4 py-2 rounded-md ${msg.sender === 'user' ? 'bg-[#212121] text-white' : 'bg-black text-gray-100'}`} style={msg.sender !== 'user' ? {fontFamily:'GruvBox'}:{}}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* Input Bar */}

      <motion.div className=' flex w-full justify-center mt-3' initial={{y: 0}} animate={isChatStarted ? {y: 50}: {y:0}} transition={{ease:'easeInOut', duration:0.5}}>
        <div className='flex items-center bg-[#404040] rounded-md px-2 justify-center py-1 w-1/2' style={{fontFamily:'GruvBox'}}>
          <input
            type='text'
            placeholder='Lets Go... Start Purring'
            className='flex-1 h-12 py-2 pl-4 rounded-md text-white placeholder-gray-400 bg-transparent focus:outline-none'
            value={inputText}
            onChange={(e)=>setInputText(e.target.value)}
            onKeyDown={(e)=>{
              if(e.key === 'Enter'){
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button onClick={handleAttachmentClick} className='p-2 rounded hover:bg-[#505050] transition ml-2 cursor-pointer'>
            <img className='w-10 invert-75' src="attach.svg" alt="" />
          </button>
          <button onClick={handleSend} className='p-2 rounded mr-2 hover:bg-[#505050] transition ml-2 cursor-pointer flex items-center justify-center'>
            <ArrowRight className='invert' />
          </button>
          <button onClick={()=>setActive(1)} className={`p-3 mr-2 cursor-pointer rounded-lg transition-all duration-200 ${active === 1 ? 'bg-black border border-white/50': ' opacity-60'}`}>
          <img className='w-6 ml-1 invert-75' src="seach1.svg" alt="" />
        </button>
        <button onClick={()=>setActive(0)} className={`p-3 w-20 l cursor-pointer rounded-lg transition-all duration-200 ${active === 0 ? 'bg-black border border-white/50': ' opacity-60'}`}>
          <img className='w-6 ml-3.5 invert-75' src="brain.svg" alt="" />
        </button>
          {/* Hidden */}
          <input type="file" ref={fileInputRef} style={{display:'none'}} multiple onChange={hadnleFileChange} />
        </div>
      </motion.div>

      {/* Toggle */}

      
    </div>
  )
}

export default ChatWIndow