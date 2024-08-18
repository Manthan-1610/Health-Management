import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/Header.css';

function Header() {
    const navigate = useNavigate();
    const isAuthenticated = localStorage.getItem('token') !== null;

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        navigate('/login');
    };

    return (
        <header className="header">
            <div className="logo">
                <h1>MyApp</h1>
            </div>
            <nav>
                <ul>
                    {isAuthenticated ? (
                        <>
                            <li><Link to="/dashboard">Dashboard</Link></li>
                            <li><button onClick={handleLogout}>Logout</button></li>
                        </>
                    ) : (
                        <>
                            <li><Link to="/login">Login</Link></li>
                            <li><Link to="/signup">Sign Up</Link></li>
                        </>
                    )}
                </ul>
            </nav>
        </header>
    );
}

export default Header;