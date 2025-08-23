import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom';

const SignUp = () => {
    const [email,setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();
    const handleSignUp = async () =>{
        try {
            const res = await axios.post("http://localhost:8000/users",{
                email,
                password
            });
            alert("User created : " + res.data.email);
        } catch (error) {
            console.log(error);
            alert("Error: " + error.response?.data?.detail || "Something went Wrong")
            
        }
    }

  return (
    <div className='h-screen flex flex-col items-center justify-center bg-black'>
      <button onClick={()=> navigate('/')}  style={{fontFamily:'GruvBox'}} className='cursor-pointer text-white absolute top-5 left-5 text-2xl'>purrXelity</button>
      <h1 className='text-white -translate-y-35 flex   text-3xl'>Welcome to purrXelity</h1>
      <div className='bg-gray-200 items-center justify-center w-95 p-2 -translate-y-25 rounded-lg shadow-lg'>
        <input onChange={(e)=> setEmail(e.target.value)} type="email" placeholder='Email' className='w-full rounded text-black focus:outline-none  ' />
      </div>
      <div className='bg-gray-200 mt-5 items-center justify-center w-95 p-2 -translate-y-25 rounded-lg shadow-lg'>
        <input onChange={(e)=>setPassword(e.target.value)} type="password" placeholder='Password' className='w-full rounded text-black focus:outline-none  ' />
      </div>      
      <span onClick={()=>navigate('/login')} className=" cursor-pointer hover:text-blue-200 text-white -translate-y-22 -translate-x-32 ">Already a User?</span>
      
      <button onClick={handleSignUp} style={{fontFamily:'GruvBox'}} className='bg-gray-100 flex -translate-y-18 items-center justify-center cursor-pointer hover:bg-amber-100  rounded-lg w-24 h-10 '>SignUp</button>
      
    </div>
  )
}

export default SignUp