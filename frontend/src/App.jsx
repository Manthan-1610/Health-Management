import React from 'react';
import '../src/styles/App.css';

function App() {
  return (
    <div className="App">
      <main>
        <section className="hero animate-slide-up">
          <h2>Your Personal Health Assistant</h2>
          <p>Manage your health with ease using AI-powered recommendations and tracking</p>
          <button className="cta-button pulse">Get Started</button>
        </section>
        <section className="features">
          <h3 className="animate-fade-in">Key Features</h3>
          <div className="feature-grid">
            <div className="feature-item animate-pop-in">
              <i className="fas fa-pills"></i>
              <h4>Medicine Suggestions</h4>
              <p>Get personalized medicine recommendations based on your symptoms</p>
            </div>
            <div className="feature-item animate-pop-in">
              <i className="fas fa-heartbeat"></i>
              <h4>Lifestyle Recommendations</h4>
              <p>Receive tailored lifestyle and diet suggestions for better health</p>
            </div>
            <div className="feature-item animate-pop-in">
              <i className="fas fa-clipboard-list"></i>
              <h4>Medicine Tracking</h4>
              <p>Keep track of your medicines, including expiry dates and dosage</p>
            </div>
            <div className="feature-item animate-pop-in">
              <i className="fas fa-chart-line"></i>
              <h4>Health Analytics</h4>
              <p>View insights and analytics about your health and medicine usage</p>
            </div>
          </div>
        </section>
      </main>
      <footer className="animate-fade-in">
        <p>&copy; 2024 Health Synce. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;