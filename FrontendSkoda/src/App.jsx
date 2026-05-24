import { useState } from "react";

import Navbar from "./components/Navbar";
import Home from "./components/Home";
import About from "./components/About";
import Footer from "./components/Footer";

import "./style.css";

function App() {

  const [page, setPage] = useState("home");

  return (
    <>
      <Navbar setPage={setPage} />

      {page === "home" ? <Home /> : <About />}

      <Footer />
    </>
  );
}

export default App;