import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/Inventory.css';

const Inventory = () => {
  const [inventory, setInventory] = useState([]);
  const [medicineName, setMedicineName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [expiryDate, setExpiryDate] = useState('');

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5070/get_inventory', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInventory(response.data);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    }
  };

  const handleAddMedicine = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const groupId = localStorage.getItem('group_id');
      await axios.post('http://localhost:5070/add_medicine', {
        group_id: groupId,
        medicine_name: medicineName,
        quantity: parseInt(quantity),
        expiry_date: expiryDate,
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Medicine added successfully!');
      setMedicineName('');
      setQuantity('');
      setExpiryDate('');
      fetchInventory();
    } catch (error) {
      console.error('Error adding medicine:', error);
      alert('Failed to add medicine.');
    }
  };

  return (
    <div className="inventory-container">
      <h2>Inventory</h2>
      <form onSubmit={handleAddMedicine}>
        <input
          type="text"
          placeholder="Medicine Name"
          value={medicineName}
          onChange={(e) => setMedicineName(e.target.value)}
          required
        />
        <input
          type="number"
          placeholder="Quantity"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          required
        />
        <input
          type="date"
          placeholder="Expiry Date"
          value={expiryDate}
          onChange={(e) => setExpiryDate(e.target.value)}
          required
        />
        <button type="submit">Add Medicine</button>
      </form>
      <table>
        <thead>
          <tr>
            <th>Medicine Name</th>
            <th>Quantity</th>
            <th>Expiry Date</th>
            <th>Added By</th>
            <th>Added At</th>
          </tr>
        </thead>
        <tbody>
          {inventory.map((item) => (
            <tr key={item.id}>
              <td>{item.medicine_name}</td>
              <td>{item.quantity}</td>
              <td>{new Date(item.expiry_date).toLocaleDateString()}</td>
              <td>{item.added_by_email}</td>
              <td>{new Date(item.added_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Inventory;