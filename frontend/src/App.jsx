import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './HomePage.jsx'
import Search from './Search.jsx'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<Search />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
