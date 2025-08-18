import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [result, setResult] = useState(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setResult(null); // clear old result
  }

  const handleUpload = async () => {
    if (!file) return alert("No file selected")
    const formData = new FormData()
    formData.append('file', file)
    await sendToBackend(formData)
  }

  const sendToBackend = async (formData) => {
    try {
      setLoading(true)
      const res = await axios.post('https://ocr-ai-zncw.onrender.com//upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setResult(res.data)
    } catch (err) {
      console.error("Error uploading:", err)
      alert("Failed to upload. Is backend running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className='header'>
        <h1>DocScan</h1>
      </div>
      <hr className='thin-line'></hr>

      <div className='font-info'>
        <p className="description">
          Upload a document to extract structured data using OCR and AI.
          <br />
          Supported formats: PDF, PNG, JPG, JPEG.
        </p>
      </div>

      <div className="upload-box">
        <label className="browse-btn">
          Choose File
          <input type="file" onChange={handleFileChange} style={{ display: "none" }} />
        </label>

        {file && (
          <p className="file-name">
            Selected: <strong>{file.name}</strong>
          </p>
        )}

        <button
          className="upload-btn"
          onClick={handleUpload}
          disabled={!file || loading}
          style={{ opacity: (!file || loading) ? 0.6 : 1 }}
        >
          {loading ? 'Uploading...' : 'Upload File'}
        </button>
      </div>

    

  ``{result && (
    <div className="output-container">
      <h3>Extracted Fields</h3>
      <div className="json-view">
        {Object.entries(result).map(([key, value]) => (
          <div key={key} className="json-field">
            <strong>{key}:</strong>{" "}
            {Array.isArray(value) ? (
              <ul className="json-list">
                {value.map((item, index) => (
                  <li key={index}>
                    <pre>{JSON.stringify(item, null, 2)}</pre>
                  </li>
                ))}
              </ul>
            ) : typeof value === "object" ? (
              <pre>{JSON.stringify(value, null, 2)}</pre>
            ) : (
              <span>{value}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )}``

    </div>
  )
}

export default App
