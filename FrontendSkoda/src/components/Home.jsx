import { useState } from "react";

function Home() {

  const [popup, setPopup] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setPopup(true);
  };

  return (
    <div className="container">

      <div className="hero">

        <h1>Skoda Voice Assistant</h1>

        <p>
          AI-powered customer lead automation platform
        </p>

      </div>

      <form className="lead-form" onSubmit={handleSubmit}>

        <h2>Customer Lead Form</h2>

        <input
          type="text"
          placeholder="Full Name"
          pattern="[A-Za-z ]+"
          maxLength="200"
          required
        />

        <input
          type="tel"
          placeholder="10 Digit Mobile Number"
          pattern="[0-9]{10}"
          required
        />

        <input
          type="email"
          placeholder="Email ID"
          required
        />

        <textarea
          placeholder="Address"
          required
        ></textarea>

        <input
          type="text"
          placeholder="Landmark (Optional)"
        />

        <input
          type="text"
          placeholder="City"
          required
        />

        <input
          type="text"
          placeholder="State"
          required
        />

        <input
          type="text"
          placeholder="Country"
          required
        />

        <input
          type="text"
          placeholder="Pincode"
          pattern="[0-9]{6}"
          required
        />

        <select required>
          <option>Select Language</option>
          <option>English</option>
          <option>Hindi</option>
          <option>Bengali</option>
          <option>Marathi</option>
          <option>Telugu</option>
          <option>Tamil</option>
          <option>Kannada</option>
          <option>Gujarati</option>
        </select>

        <select required>
          <option>Interaction Mode</option>
          <option>Voice</option>
          <option>Typing</option>
        </select>

        <button type="submit">
          Submit Lead
        </button>

      </form>

      {popup && (
        <div className="popup">

          <div className="popup-box">

            <h2>Lead Submitted Successfully</h2>

            <p>
              You will receive a confirmation call
              shortly from Skoda Voice Assistant.
            </p>

            <button onClick={() => setPopup(false)}>
              Close
            </button>

          </div>

        </div>
      )}

    </div>
  );
}

export default Home;