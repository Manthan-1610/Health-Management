import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [groupInfo, setGroupInfo] = useState(null);
  const [groupMembers, setGroupMembers] = useState([]);
  const [isCreator, setIsCreator] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await axios.get('http://localhost:5070/verify_token', {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (response.data.valid) {
            setIsAuthenticated(true);
            await fetchGroupInfo(token);
          }
        } catch (error) {
          console.error('Error verifying token:', error);
          localStorage.removeItem('token');
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const fetchGroupInfo = async (token) => {
    try {
      const response = await axios.get('http://localhost:5070/get_user_group', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGroupInfo(response.data);
      if (response.data.group_id) {
        await fetchGroupMembers(token);
      }
    } catch (error) {
      console.error('Error fetching group info:', error);
    }
  };

  const fetchGroupMembers = async (token) => {
    try {
      const response = await axios.get('http://localhost:5070/get_group_members', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGroupMembers(response.data.members);
      setIsCreator(response.data.is_creator);
    } catch (error) {
      console.error('Error fetching group members:', error);
    }
  };

  const handleRemoveMember = async (memberId) => {
    if (!isCreator) {
      alert("Only the group creator can remove members.");
      return;
    }
    if (window.confirm('Are you sure you want to remove this member?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.post('http://localhost:5070/remove_group_member', 
          { member_id: memberId },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        await fetchGroupMembers(token);
      } catch (error) {
        console.error('Error removing member:', error);
        alert("Failed to remove member. You may not have permission.");
      }
    }
  };

  const handleDeleteGroup = async () => {
    if (!isCreator) {
      alert("Only the group creator can delete the group.");
      return;
    }
    if (window.confirm('Are you sure you want to delete the entire group?')) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post('http://localhost:5070/delete_group', 
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (response.status === 200) {
          alert("Group deleted successfully");
          setGroupInfo(null);
          setGroupMembers([]);
          setIsCreator(false);
        } else {
          alert(`Failed to delete group: ${response.data.error}`);
        }
      } catch (error) {
        console.error('Error deleting group:', error);
        if (error.response) {
          alert(`Failed to delete group: ${error.response.data.error}`);
        } else {
          alert("Failed to delete group. An unexpected error occurred.");
        }
      }
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div className="dashboard-container">
      <h2>Welcome to Your Dashboard</h2>
      {groupInfo && groupInfo.group_id ? (
        <>
          <p>You are in the group: {groupInfo.group_name}</p>
          <h3>Group Members</h3>
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Phone Number</th>
                {isCreator && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {groupMembers.map(member => (
                <tr key={member.id}>
                  <td>{member.email}</td>
                  <td>{member.phone_number}</td>
                  {isCreator && member.id !== member.creator_id && (
                    <td>
                      <button onClick={() => handleRemoveMember(member.id)}>Remove</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
          {isCreator && (
            <button onClick={handleDeleteGroup}>Delete Group</button>
          )}
        </>
      ) : (
        <p>You are not in any group yet.</p>
      )}
      <nav>
        <ul>
          <li><Link to="/inventory">Inventory</Link></li>
          <li><Link to="/familygroup">Family Group</Link></li>
        </ul>
      </nav>
    </div>
  );
};

export default Dashboard;