from flask import Flask, render_template, request, jsonify, session
from langchain_core.messages import HumanMessage, AIMessage
import os
from agent import get_agent

app = Flask(__name__)
app.secret_key = os.urandom(24) # For session storage

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    # Ensure a session exists
    session.permanent = True 
    if 'chat_history' not in session:
        session['chat_history'] = []
        
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
        
    # Reconstruct chat history for LangChain
    chat_history = []
    for msg in session['chat_history']:
        if msg['role'] == 'user':
            chat_history.append(HumanMessage(content=msg['content']))
        else:
            chat_history.append(AIMessage(content=msg['content']))
            
    try:
        agent_executor = get_agent()
        messages_input = chat_history + [HumanMessage(content=user_input)]
        response = agent_executor.invoke({
            "messages": messages_input
        })
        
        bot_reply = response['messages'][-1].content
        
        # Update session memory safely
        current_history = session.get('chat_history', [])
        current_history.append({'role': 'user', 'content': user_input})
        current_history.append({'role': 'assistant', 'content': bot_reply})
        # Keep history manageable (last 10 messages)
        session['chat_history'] = current_history[-10:]
        session.modified = True
        
        return jsonify({'response': bot_reply})
        
    except Exception as e:
        print(f"Error during agent invocation: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
