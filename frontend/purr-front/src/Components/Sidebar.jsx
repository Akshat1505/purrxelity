import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios';

function Sidebar({userId}) {
  const navigate = useNavigate();
  const [chats, setChats] = useState([]);

  useEffect(()=>{
    const fetchChats = async ()=> {
      try { 
        const userId = 1;
        const res = await axios.get(`http://localhost:8000/users/${userId}/chats`);
        setChats(res.data);
      } catch (error) {
        console.error('Error fetching chats' , error); 
      }
    };
    fetchChats();
  }, []);

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
      <div className='group-hover:justify-center flex justify-start transition-opacity-250 '>
        <span className='text-xs group-hover:text-lg transition-all duration-250 justify-center mb-125'>History</span>
      </div>
    </div>
  )
}

export default Sidebar