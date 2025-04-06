import React, { useState, useEffect, useRef } from 'react';
import './index.css';

function App() {
  const [notes, setNotes] = useState([]);
  const [activeNote, setActiveNote] = useState(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [cursorPosition, setCursorPosition] = useState(0);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [currentWord, setCurrentWord] = useState('');
  const textAreaRef = useRef(null);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const response = await fetch('https://smart-notes-webapp.onrender.com/api/notes');
      const data = await response.json();
      setNotes(data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  };

  const saveNote = async () => {
    if (!title.trim()) return;

    try {
      const noteData = {
        title,
        content,
        created_at: new Date().toISOString()
      };

      let response;
      if (activeNote) {
        response = await fetch(`https://smart-notes-webapp.onrender.com/api/notes/${activeNote.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(noteData)
        });
      } else {
        response = await fetch('https://smart-notes-webapp.onrender.com/api/notes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(noteData)
        });
      }

      const savedNote = await response.json();
      
      await fetch('https://smart-notes-webapp.onrender.com/api/learn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: title + ' ' + content })
      });
      
      fetchNotes();
      if (!activeNote) {
        clearForm();
      } else {
        setActiveNote(savedNote);
      }
    } catch (error) {
      console.error('Error saving note:', error);
    }
  };

  const deleteNote = async (id) => {
    try {
      await fetch(`https://smart-notes-webapp.onrender.com/api/notes/${id}`, {
        method: 'DELETE'
      });
      fetchNotes();
      if (activeNote && activeNote.id === id) {
        clearForm();
      }
    } catch (error) {
      console.error('Error deleting note:', error);
    }
  };

  const clearForm = () => {
    setActiveNote(null);
    setTitle('');
    setContent('');
  };

  const editNote = (note) => {
    setActiveNote(note);
    setTitle(note.title);
    setContent(note.content);
  };

  const fetchSuggestions = async (word) => {
    if (!word || word.length < 1) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    try {
      const response = await fetch(`https://smart-notes-webapp.onrender.com/api/autocomplete?prefix=${word}`);
      const data = await response.json();
      setSuggestions(data);
      setShowSuggestions(data.length > 0);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const handleContentChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    
    const position = e.target.selectionStart;
    setCursorPosition(position);
    
    const textBeforeCursor = newContent.substring(0, position);
    const words = textBeforeCursor.split(/\s+/);
    const word = words[words.length - 1].toLowerCase();
    
    setCurrentWord(word);
    fetchSuggestions(word);
  };

  const applySuggestion = (suggestion) => {
    const textBeforeCursor = content.substring(0, cursorPosition);
    const textAfterCursor = content.substring(cursorPosition);
    
    const lastSpaceBeforeCursor = textBeforeCursor.lastIndexOf(' ') + 1;
    const wordStart = textBeforeCursor.substring(0, lastSpaceBeforeCursor);
    
    const newContent = wordStart + suggestion.word + ' ' + textAfterCursor;
    setContent(newContent);
    
    const newPosition = wordStart.length + suggestion.word.length + 1;
    setTimeout(() => {
      if (textAreaRef.current) {
        textAreaRef.current.focus();
        textAreaRef.current.selectionStart = newPosition;
        textAreaRef.current.selectionEnd = newPosition;
      }
    }, 0);
    
    setShowSuggestions(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab' && showSuggestions && suggestions.length > 0) {
      e.preventDefault();
      applySuggestion(suggestions[0]);
    }
  };

  return (
    <div className="min-h-screen bg-black text-gray-100 flex">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 p-4 border-r border-gray-700">
        <h1 className="text-2xl font-bold mb-6 text-yellow-100">Smart Notes</h1>
        <button 
          onClick={clearForm}
          className="mb-4 px-4 py-2 bg-yellow-100 text-black rounded hover:bg-yellow-200 w-full font-medium"
        >
          New Note
        </button>
        
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2 text-yellow-100">Your Notes</h2>
          {notes.length === 0 ? (
            <p className="text-gray-500 text-sm">No notes yet. Create one!</p>
          ) : (
            <ul className="space-y-2">
              {notes.map(note => (
                <li 
                  key={note.id} 
                  className={`p-2 rounded cursor-pointer flex justify-between ${
                    activeNote && activeNote.id === note.id 
                      ? 'bg-yellow-100 text-black' 
                      : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                >
                  <span 
                    className="truncate w-40"
                    onClick={() => editNote(note)}
                  >
                    {note.title}
                  </span>
                  <button 
                    onClick={() => deleteNote(note.id)}
                    className="text-red-400 hover:text-red-600"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 p-8">
        <div className="max-w-3xl mx-auto">
          <div className="mb-6">
            <input
              type="text"
              placeholder="Note Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-3 text-xl font-bold bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-yellow-300 text-yellow-100"
            />
          </div>
          
          <div className="relative">
            <textarea
              ref={textAreaRef}
              rows="16"
              placeholder="Start typing your note here..."
              value={content}
              onChange={handleContentChange}
              onKeyDown={handleKeyDown}
              className="w-full p-4 bg-gray-900 border border-gray-700 rounded resize-none focus:outline-none focus:border-yellow-300 leading-relaxed text-yellow-50 font-mono"
            ></textarea>
            
            {showSuggestions && (
              <div className="absolute z-10 mt-1 w-64 max-h-60 overflow-y-auto bg-gray-800 border border-gray-700 rounded shadow-lg">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    onClick={() => applySuggestion(suggestion)}
                    className="p-2 hover:bg-gray-700 cursor-pointer flex justify-between"
                  >
                    <span className="text-yellow-100">{suggestion.word}</span>
                    <span className="text-gray-500 text-xs">{suggestion.frequency}</span>
                  </div>
                ))}
                <div className="p-2 text-xs text-gray-500 border-t border-gray-700">
                  Press Tab to autocomplete
                </div>
              </div>
            )}
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              onClick={saveNote}
              className="px-6 py-2 bg-yellow-100 text-black rounded hover:bg-yellow-200 font-medium"
            >
              {activeNote ? 'Update Note' : 'Save Note'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;