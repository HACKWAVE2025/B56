import React from 'react';
import './ToggleSwitch.css';

const ToggleSwitch = ({ id, isToggled, handleToggle, label }) => {
  return (
    <div className="flex items-center justify-between my-2">
      <label htmlFor={id} className="mr-4 text-gray-700 font-semibold">{label}</label>
      <label className="toggle-switch">
        <input 
          type="checkbox" 
          id={id}
          checked={isToggled} 
          onChange={handleToggle} 
        />
        <span className="slider"></span>
      </label>
    </div>
  );
};

export default ToggleSwitch;
