
import { useRef } from "react";
import "./Home.css"
import axios from "axios";
import { NavLink } from "react-router-dom";
export default function HomeView() {
 

    return(
        <section className="body">
        
            <div style={{"width":"100vw","padding":"20px 30px","height":"100vh","display":"flex","flexFlow":"column","justifyContent":"start","alignItems":"start"}}>
                <h1>Dashboard</h1>
                <NavLink className='btn btn-neutral' to={"/registration"}>Register</NavLink>
               
           </div>
        </section>
     );
}