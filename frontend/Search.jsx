import { useState, useEffect } from 'react';
import axios from 'axios';
import { MdHome } from "react-icons/md";
import './App.css';
import { useNavigate } from 'react-router-dom';
import { FaDatabase } from "react-icons/fa6";

function Search() {
  const navigate = useNavigate();
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get('https://ocr-ai-zncw.onrender.com/history')
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="container">
      <div className="header">
        <h1>Document History</h1>
        <button className="home-btn" onClick={() => navigate('/')}>
          <MdHome /> Home
        </button>
      </div>

      <hr />

      <div className='font-info'>
        <p className="description">
          View and search metadata for the documents you have uploaded.
        </p>
      </div>

      <table>
        <thead>
          <tr>
            <th>Filename</th>
            <th>Table Data</th>
            <th>Structured JSON</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.filename}>
              <td>{row.filename}</td>
              <td><pre>{JSON.stringify(row.table_data, null, 2)}</pre></td>
              <td><pre>{JSON.stringify(row.structured_json, null, 2)}</pre></td>
              <td>{row.created_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Search;
