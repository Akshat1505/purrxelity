import shutil
import docker,json,os,uuid
from langchain.tools import BaseTool
from typing import Optional,Literal
from langchain_core.tools import ArgsSchema
from pydantic import BaseModel,Field

class CodeExecutorInput(BaseModel):
    language:Literal["cpp","python","rust"]=Field(description="code language, must be one of 'cpp','python','rust'")
    code:str=Field(description="valid code to be executed")

class CodeExecutor(BaseTool):
    name:str="CodeExecutor"
    description:str=(
        "Executes code in a secure docker container"
        "supported languages are 'cpp','python,'rust'"
        "function takes two arguements 'language' and 'code'"
    )
    args_schema:Optional[ArgsSchema]=CodeExecutorInput
    return_direct:bool=False

    DOCKER_IMAGE:str = "multi-lang-executor" 
    def _run(self,language:Literal["cpp","python","rust"],code:str):
        templates={
            "cpp":{
                "filename":"main.cpp",
                "compile":"g++ main.cpp -o main -std=c++17",
                "run":"./main"
            },
            "python":{
                "filename":"script.py",
                "compile":None,
                "run":"python3 script.py"
            },
            "rust":{
                "filename":"main.rs",
                "compile":"rustc main.rs -o main",
                "run":"./main"
            }
        }
        client=docker.from_env()
        temp_dir=os.path.join("/tmp",f"code-exe-f{uuid.uuid4()}")
        os.makedirs(temp_dir,exist_ok=True)

        try:
            filepath = os.path.join(temp_dir, templates[language]['filename'])
            with open(filepath, "w") as f:
                f.write(code)    
            full_cmd=" && ".join(filter(None,[templates[language]["compile"],templates[language]["run"]]))
            result=client.containers.run(
                image=self.DOCKER_IMAGE,
                command=f'/bin/sh -c "timeout 10 {full_cmd}"',
                volumes={temp_dir: {'bind': '/app', 'mode': 'rw'}},
                working_dir='/app',
                pids_limit=20,
                mem_limit='512m',
                remove=True,
                stdout=True,
                stderr=True,
                network_disabled=True,
            )
            return result.decode('utf-8').strip()
        except Exception as e:
            print(f"Code execution : {str(e)} ")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                    


