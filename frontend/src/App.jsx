import React from 'react';
import Header from './components/Header';
import LogInteractionScreen from './components/LogInteractionScreen';

export default function App() {
  return (
    <div className="app-shell">
      <Header />
      <LogInteractionScreen />
    </div>
  );
}