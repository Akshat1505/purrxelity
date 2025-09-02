import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios';

function Sidebar({userId}) {
  const navigate = useNavigate();
  const [chats, setChats] = useState([]);

  useEffect(()=>{
    const fetchChats = async ()=> {
      try { 
        const res = await axios.get(`http://localhost:8000/users/${userId}/chats`);
        setChats(res.data);
      } catch (error) {
        console.error('Error fetching chats' , error); 
      }
    };
    fetchChats();
  }, [userId]);

  return (
    <div style={{fontFamily:'GruvBox'}} className='group w-18 cursor-pointer hover:w-50 transition-all duration-250 text-white h-screen bg-[#282828] p-4 flex flex-col justify-between fixed top-0  '>
      <div className='flex justify-start group-hover:justify-center transition-all duration-250'>
        <img src="logo1.svg" alt="" className='w-18 invert' />
      </div>
      <button onClick={()=> navigate('/chat/new')}  className='flex  justify-start group-hover:justify-center items-center space-x-2 text-white text-sm hover:text-gray-300'>
        <div className=' min-w-10 h-10 border border-white rounded-lg flex items-center justify-center'>
          <img className=' w-10 invert cursor-pointer ' src="plus-svgrepo-com.svg" alt="" />
        </div>
        <span className='opacity-0 group-hover:opacity-100 transition-opacity-250'>New Chat</span>
      </button>
      <div className='w-full mt-4 '>
       <div className='flex flex-col items-start w-full'>
         <span className='text-xs group-hover:text-lg transition-all duration-250 justify-center mb-2'>History</span>
          <div className='w-full flex flex-col space-y-2 overflow-y-auto max-h-[60vh] pr-2 '>
            {chats.length > 0 ? (
              chats.map((chat)=>{
                let preview = "Untitled Chat";
                try {
                  let msgs = chat.messages;
                  if(typeof msgs === 'string'){
                    msgs= JSON.parse(msgs);
                  };
                  if(Array.isArray(msgs) && msgs.length > 0){
                    const firstUserMsg = msgs.find(m=> m.role && String(m.role).toLowerCase()=== 'user');
                    const cand = firstUserMsg || msgs[0];
                    if(cand && cand.content){
                      preview = String(cand.content).slice(0,30);
                    }
                  }else{
                    console.warn('Sidebar: unexpected messages shape for thread', chat.thread_id, msgs);
                  }
                } catch (e) {
                  console.error("Error Parsing Messages",chat.thread_id,e,'raw',chat.messages);
                  
                }
                return(
                  <button key={chat.thread_id} onClick={()=> navigate(`/chat/${chat.thread_id}`)} className='w-full px-3 py-6 mb-1 text-sm text-left cursor-pointer hover:bg-[#3a3a3a] rounded truncate hover:text-gray-400' title={preview}>{preview}</button>
                )
              })
            ) : (
              <span className='text-gray-600 text-xs'>No Chats yet</span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar