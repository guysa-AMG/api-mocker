
import { useRef } from "react";
import "./Home.css"
import axios from "axios";
import { NavLink } from "react-router-dom";

export default function RegistrationView() {
    let fileref  = useRef(null);
    let nameref  = useRef(null);
    let submit = ()=>{
      let form = new FormData();

      if(nameref.current==null || fileref.current==null){ return; }

      form.append("name",nameref.current!);
      form.append("file",fileref.current!);
      axios.post("localhost:8000/register",form)
    }


    return(
        <section className="body">
        
            <div style={{"width":"100vw","height":"100vh","display":"flex","justifyContent":"center","alignItems":"center"}}>
                <article style={{"display":"flex","flexFlow":"column","gap":"20px"}}>
                <NavLink to={"/home"}>
                👈🏼
                </NavLink>
                  <h1>apidoc registration</h1>
                <input type="text" ref={nameref} placeholder="Api Name" className="input w-full max-w-xs" />
             <input type="file" ref={fileref} placeholder="openAPI spec file"  className="input w-full max-w-xs" />
             
                <button className='btn btn-info' onClick={submit}>Submit</button>
                </article></div>
        </section>
     );
}