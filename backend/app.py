from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)  

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.frequency = 0
        self.word = None

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        """Insert a word into the trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.frequency += 1
        node.word = word
    
    def search(self, word):
        """Search for a word in the trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word
    
    def starts_with_prefix(self, prefix):
        """Find all words that start with the given prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Now find all words with this prefix
        suggestions = []
        self._find_all_words(node, suggestions)
        # Sort by frequency, highest first
        suggestions.sort(key=lambda x: x['frequency'], reverse=True)
        return suggestions[:10]  # Limit to top 10 suggestions
    
    def _find_all_words(self, node, suggestions):
        """Recursively find all words from the given node"""
        if node.is_end_of_word:
            suggestions.append({'word': node.word, 'frequency': node.frequency})
        
        for char, child_node in node.children.items():
            self._find_all_words(child_node, suggestions)

# Initialize the trie
trie = Trie()

# Load initial dictionary (could be from a file)
initial_words = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "I", 
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "python", "flask", "trie", "data", "structure", "algorithm", "programming",
    "web", "application", "notes", "autocomplete", "system", "design",
    
    "are", "is", "was", "were", "been", "being", "am", "has", "had", "having",
    "do", "does", "did", "doing", "can", "could", "should", "would", "may", "might",
    "must", "shall", "will", "should", "want", "need", "like", "make", "know", "think",
    "take", "see", "come", "look", "want", "find", "give", "tell", "work", "call",
    "try", "ask", "use", "seem", "feel", "become", "leave", "put", "mean", "keep",
    "let", "begin", "help", "talk", "turn", "start", "show", "hear", "play", "run",
    "move", "live", "believe", "bring", "happen", "write", "provide", "sit", "stand",
    "lose", "pay", "meet", "include", "continue", "set", "learn", "change", "lead",
    "understand", "watch", "follow", "stop", "create", "speak", "read", "allow",
    "add", "spend", "grow", "open", "walk", "win", "offer", "remember", "love",
    "consider", "appear", "buy", "wait", "serve", "die", "send", "expect", "build",
    "stay", "fall", "cut", "reach", "kill", "remain", "suggest", "raise", "pass",
    "sell", "require", "report", "decide", "pull", "return",
    
    "note", "notes", "idea", "ideas", "thought", "thoughts", "concept", "concepts",
    "summary", "summaries", "outline", "outlines", "bullet", "bullets", "point", "points",
    "topic", "topics", "subject", "subjects", "theme", "themes", "reminder", "reminders",
    "task", "tasks", "action", "actions", "project", "projects", "priority", "priorities",
    "deadline", "deadlines", "date", "dates", "schedule", "schedules", "meeting", "meetings",
    "appointment", "appointments", "important", "urgent", "later", "soon", "tomorrow", "today",
    "yesterday", "week", "month", "year", "morning", "afternoon", "evening", "night",
    "daily", "weekly", "monthly", "yearly", "recurring", "once", "twice", "review", "follow-up",
    
    "research", "study", "analysis", "report", "paper", "article", "journal", "conference",
    "presentation", "lecture", "class", "course", "assignment", "exam", "test", "quiz",
    "grade", "score", "result", "outcome", "conclusion", "introduction", "methodology",
    "discussion", "reference", "citation", "source", "literature", "theory", "hypothesis",
    "experiment", "data", "statistics", "figure", "table", "chart", "graph", "diagram",
    "illustration", "example", "definition", "term", "concept", "principle", "method",
    "technique", "approach", "strategy", "plan", "objective", "goal", "purpose", "function",
    "role", "significance", "importance", "impact", "effect", "cause", "reason", "explanation",
    "analysis", "evaluation", "assessment", "review", "critique", "argument", "evidence",
    "support", "justify", "demonstrate", "show", "indicate", "suggest", "imply", "infer",
    
    "meeting", "agenda", "minutes", "action", "item", "decision", "approval", "review",
    "status", "update", "progress", "milestone", "deliverable", "timeline", "schedule",
    "deadline", "budget", "cost", "expense", "resource", "allocation", "assignment",
    "responsibility", "role", "stakeholder", "client", "customer", "vendor", "supplier",
    "partner", "collaboration", "teamwork", "feedback", "input", "output", "outcome",
    "result", "performance", "metric", "measure", "indicator", "target", "goal", "objective",
    "strategy", "tactic", "plan", "implementation", "execution", "operation", "process",
    "procedure", "policy", "guideline", "standard", "quality", "improvement", "optimization",
    "efficiency", "effectiveness", "productivity", "innovation", "development", "growth",
    
    "happy", "sad", "angry", "frustrated", "excited", "nervous", "anxious", "calm",
    "peaceful", "stressed", "overwhelmed", "motivated", "inspired", "discouraged", "hopeful",
    "grateful", "thankful", "proud", "embarrassed", "confused", "curious", "interested",
    "bored", "tired", "energized", "relaxed", "tense", "worried", "relieved", "surprised",
    "disappointed", "satisfied", "content", "upset", "emotional", "feeling", "mood", "attitude",
    "mindset", "perspective", "outlook", "view", "opinion", "belief", "value", "principle",
    "reflection", "introspection", "meditation", "awareness", "mindfulness", "presence",
    "focus", "attention", "distraction", "concentration", "memory", "recall", "forget",
    "remember", "learn", "understand", "realize", "recognize", "acknowledge", "accept"
]

# Insert all initial words
for word in initial_words:
    trie.insert(word)

# In-memory storage for notes (replace with database in production)
notes = []

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    """Get autocomplete suggestions for the given prefix"""
    prefix = request.args.get('prefix', '')
    if not prefix or len(prefix) < 1:
        return jsonify([])
    
    suggestions = trie.starts_with_prefix(prefix.lower())
    return jsonify(suggestions)

@app.route('/api/learn', methods=['POST'])
def learn_words():
    """Learn new words from user input"""
    data = request.get_json()
    text = data.get('text', '')
    
    # Simple word extraction - in a real app, you'd want more sophisticated parsing
    words = text.lower().split()
    for word in words:
        # Clean word of punctuation
        clean_word = ''.join(c for c in word if c.isalnum())
        if clean_word and len(clean_word) > 1:  # Ignore single characters
            trie.insert(clean_word)
    
    return jsonify({"status": "success", "words_learned": len(words)})

@app.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    """Get all notes or create a new note"""
    if request.method == 'GET':
        return jsonify(notes)
    
    if request.method == 'POST':
        data = request.get_json()
        note = {
            'id': len(notes) + 1,
            'title': data.get('title', 'Untitled'),
            'content': data.get('content', ''),
            'created_at': data.get('created_at', '')
        }
        notes.append(note)
        
        # Learn words from the note
        text = note['title'] + ' ' + note['content']
        words = text.lower().split()
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word and len(clean_word) > 1:
                trie.insert(clean_word)
        
        return jsonify(note)

@app.route('/api/notes/<int:note_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_note(note_id):
    """Get, update or delete a specific note"""
    note_index = next((index for index, note in enumerate(notes) if note['id'] == note_id), None)
    
    if note_index is None:
        return jsonify({"error": "Note not found"}), 404
    
    if request.method == 'GET':
        return jsonify(notes[note_index])
    
    if request.method == 'PUT':
        data = request.get_json()
        notes[note_index]['title'] = data.get('title', notes[note_index]['title'])
        notes[note_index]['content'] = data.get('content', notes[note_index]['content'])
        
        # Learn new words from the updated note
        text = notes[note_index]['title'] + ' ' + notes[note_index]['content']
        words = text.lower().split()
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word and len(clean_word) > 1:
                trie.insert(clean_word)
        
        return jsonify(notes[note_index])
    
    if request.method == 'DELETE':
        deleted_note = notes.pop(note_index)
        return jsonify(deleted_note)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)