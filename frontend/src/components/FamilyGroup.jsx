import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/FamilyGroup.css';

const FamilyGroup = () => {
  const [groupName, setGroupName] = useState('');
  const [inviteePhone, setInviteePhone] = useState('');
  const [invitations, setInvitations] = useState([]);
  const [userGroupId, setUserGroupId] = useState(null);

  useEffect(() => {
    fetchUserGroupId();
    fetchInvitations();
  }, []);

  const fetchUserGroupId = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5070/get_user_group', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserGroupId(response.data.group_id);
      localStorage.setItem('group_id', response.data.group_id);
    } catch (error) {
      console.error('Error fetching user group:', error);
    }
  };

  const fetchInvitations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5070/get_invitations', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInvitations(response.data);
    } catch (error) {
      console.error('Error fetching invitations:', error);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5070/create_family_group', {
        group_name: groupName,
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Family group created successfully!');
      setUserGroupId(response.data.group_id);
      localStorage.setItem('group_id', response.data.group_id);
      setGroupName('');
    } catch (error) {
      console.error('Error creating family group:', error);
      alert('Failed to create family group.');
    }
  };

  const handleInviteMember = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5070/invite_family_member', {
        receiver_phone: inviteePhone,
        group_id: userGroupId,
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Invitation sent successfully!');
      setInviteePhone('');
    } catch (error) {
      console.error('Error inviting family member:', error);
      alert('Failed to send invitation.');
    }
  };

  const handleRespondToInvitation = async (invitationId, response) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5070/respond_to_invitation', {
        invitation_id: invitationId,
        response: response,
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert(`Invitation ${response}ed successfully!`);
      fetchInvitations();
      if (response === 'accept') {
        fetchUserGroupId();
      }
    } catch (error) {
      console.error('Error responding to invitation:', error);
      alert('Failed to respond to invitation.');
    }
  };

  return (
    <div className="family-group-container">
      <h2>Family Group</h2>
      {!userGroupId ? (
        <form onSubmit={handleCreateGroup}>
          <input
            type="text"
            placeholder="Group Name"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            required
          />
          <button type="submit">Create Family Group</button>
        </form>
      ) : (
        <div>
          <h3>Invite Family Member</h3>
          <form onSubmit={handleInviteMember}>
            <input
              type="tel"
              placeholder="Invitee Phone Number"
              value={inviteePhone}
              onChange={(e) => setInviteePhone(e.target.value)}
              required
            />
            <button type="submit">Send Invitation</button>
          </form>
        </div>
      )}
      <div className="invitations">
        <h3>Pending Invitations</h3>
        {invitations.map((invitation) => (
          <div key={invitation.id} className="invitation">
            <p>From: {invitation.sender_email}</p>
            <p>Group: {invitation.group_name}</p>
            <button onClick={() => handleRespondToInvitation(invitation.id, 'accept')}>Accept</button>
            <button onClick={() => handleRespondToInvitation(invitation.id, 'decline')}>Decline</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FamilyGroup;