
import { useRef } from "react";
import "./Home.css"
import axios from "axios";

export default function HomeView() {
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
            <div className="navbar bg-base-100">
              <div className="navbar-start">
                <div className="dropdown">
                  <label tabIndex={0} className="btn btn-ghost lg:hidden">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h8m-8 6h16" /></svg>
                  </label>
                  <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
                    <li><a>Item 1</a></li>
                    <li>
                      <a>Parent</a>
                      <ul className="p-2">
                        <li><a>Submenu 1</a></li>
                        <li><a>Submenu 2</a></li>
                      </ul>
                    </li>
                    <li><a>Item 3</a></li>
                  </ul>
                </div>
                <a className="btn btn-ghost text-xl">FauxAPI</a>
              </div>
              <div className="navbar-center hidden lg:flex">
                <ul className="menu menu-horizontal px-1">
                  <li><a>Item 1</a></li>
                  {/* <li tabIndex={0}>
                    <details>
                      <summary>Parent</summary>
                      <ul className="p-2">
                        <li><a>Submenu 1</a></li>
                        <li><a>Submenu 2</a></li>
                      </ul>
                    </details>
                  </li> */}
                  <li><a>Item 3</a></li>
                </ul>
              </div>
              <div className="navbar-end">
                <button className='btn btn-circle'></button>
              </div>
            </div >
            <div style={{"width":"100vw","height":"100vh","display":"flex","justifyContent":"center","alignItems":"center"}}>
                <article style={{"display":"flex","flexFlow":"column","gap":"20px"}}>
                <input type="text" ref={nameref} placeholder="Api Name" className="input w-full max-w-xs" />
             <input type="file" ref={fileref} placeholder="openAPI spec file"  className="input w-full max-w-xs" />
             
                <button className='btn btn-info' onClick={submit}>Submit</button>
                </article></div>
        </section>
     );
}