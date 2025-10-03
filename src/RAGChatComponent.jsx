/**
 * RAG Chat Component for Next.js
 * Drop-in component for your application
 */

import React, { useState, useEffect } from 'react';
import RAGClient from './nextjs-rag-client';

const RAGChatComponent = ({ 
  ragApiUrl = 'http://localhost:8080',
  defaultModel = 'gemini-1.5-flash',
  apiKey = null 
}) => {
  const [client] = useState(() => new RAGClient(ragApiUrl, apiKey));
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelConfig, setModelConfig] = useState({
    model_name: defaultModel,
    api_key: process.env.NEXT_PUBLIC_GEMINI_API_KEY,
    max_tokens: 512,
    temperature: 0.7
  });

  // Health check on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await client.healthCheck();
        console.log('RAG API Health:', health);
      } catch (err) {
        console.error('RAG API not available:', err);
        setError('RAG API not available');
      }
    };
    checkHealth();
  }, [client]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await client.query(input, {
        modelConfig,
        queryMetadata: {
          timestamp: new Date().toISOString(),
          source: 'web_app'
        }
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.answer,
        metadata: {
          used_rag: response.used_rag,
          complexity_score: response.complexity_score,
          reasoning: response.reasoning,
          model_used: response.model_used,
          context_blocks: response.context_blocks,
          performance_metrics: response.performance_metrics
        }
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message);
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${err.message}`,
        metadata: { error: true }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const switchModel = async (newModel) => {
    const newConfig = {
      ...modelConfig,
      model_name: newModel,
      api_key: getApiKeyForModel(newModel)
    };
    
    try {
      await client.setDefaultModel(newConfig);
      setModelConfig(newConfig);
    } catch (err) {
      setError(`Failed to switch to ${newModel}: ${err.message}`);
    }
  };

  const getApiKeyForModel = (modelName) => {
    if (modelName.includes('gemini')) {
      return process.env.NEXT_PUBLIC_GEMINI_API_KEY;
    } else if (modelName.includes('gpt')) {
      return process.env.NEXT_PUBLIC_OPENAI_API_KEY;
    } else if (modelName.includes('huggingface')) {
      return process.env.NEXT_PUBLIC_HUGGINGFACE_API_KEY;
    }
    return null;
  };

  return (
    <div className="rag-chat-container">
      {/* Model Selector */}
      <div className="model-selector">
        <label>Model: </label>
        <select 
          value={modelConfig.model_name} 
          onChange={(e) => switchModel(e.target.value)}
          disabled={loading}
        >
          <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
          <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          <option value="gpt-4">GPT-4</option>
          <option value="your-fine-tuned-model">Your Fine-tuned Model</option>
        </select>
      </div>

      {/* Messages */}
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">
              {message.content}
            </div>
            {message.metadata && !message.metadata.error && (
              <div className="message-metadata">
                <small>
                  {message.metadata.used_rag ? '🔍 RAG' : '⚡ Direct'} | 
                  Score: {message.metadata.complexity_score?.toFixed(2)} | 
                  Model: {message.metadata.model_used} | 
                  Time: {message.metadata.performance_metrics?.total_time?.toFixed(2)}s
                </small>
                {message.metadata.context_blocks?.length > 0 && (
                  <details>
                    <summary>Context Sources ({message.metadata.context_blocks.length})</summary>
                    {message.metadata.context_blocks.map((block, i) => (
                      <div key={i} className="context-block">
                        <strong>Source {i + 1}:</strong> {block.content?.substring(0, 100)}...
                      </div>
                    ))}
                  </details>
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="loading-spinner">Thinking...</div>
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
          className="message-input"
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>

      <style jsx>{`
        .rag-chat-container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: #f9f9f9;
        }

        .model-selector {
          margin-bottom: 20px;
          padding: 10px;
          background: white;
          border-radius: 4px;
        }

        .model-selector select {
          margin-left: 10px;
          padding: 5px;
        }

        .messages-container {
          max-height: 400px;
          overflow-y: auto;
          margin-bottom: 20px;
        }

        .message {
          margin-bottom: 15px;
          padding: 10px;
          border-radius: 8px;
        }

        .message.user {
          background: #007bff;
          color: white;
          margin-left: 20%;
        }

        .message.assistant {
          background: white;
          border: 1px solid #ddd;
          margin-right: 20%;
        }

        .message-content {
          margin-bottom: 5px;
        }

        .message-metadata {
          font-size: 0.8em;
          color: #666;
          margin-top: 5px;
        }

        .context-block {
          margin: 5px 0;
          padding: 5px;
          background: #f0f0f0;
          border-radius: 4px;
          font-size: 0.9em;
        }

        .loading-spinner {
          font-style: italic;
          color: #666;
        }

        .error-message {
          background: #f8d7da;
          color: #721c24;
          padding: 10px;
          border-radius: 4px;
          margin-bottom: 10px;
        }

        .input-form {
          display: flex;
          gap: 10px;
        }

        .message-input {
          flex: 1;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .input-form button {
          padding: 10px 20px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .input-form button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default RAGChatComponent;
