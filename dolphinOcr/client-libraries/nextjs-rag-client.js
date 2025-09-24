/**
 * Next.js RAG Client Library
 * Easy integration with Universal RAG API
 */

class RAGClient {
  constructor(baseUrl = 'http://localhost:8080', apiKey = null) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.defaultModel = {
      model_name: 'gemini-1.5-flash',
      api_key: process.env.NEXT_PUBLIC_GEMINI_API_KEY,
      max_tokens: 512,
      temperature: 0.7
    };
  }

  /**
   * Query the RAG system
   * @param {string} query - The question to ask
   * @param {Object} options - Query options
   * @param {Object} options.queryMetadata - Additional metadata
   * @param {Object} options.modelConfig - Model configuration
   * @param {string} options.modelConfig.model_name - Model name
   * @param {string} options.modelConfig.api_key - API key
   * @param {number} options.modelConfig.max_tokens - Max tokens
   * @param {number} options.modelConfig.temperature - Temperature
   * @returns {Promise<Object>} RAG response
   */
  async query(query, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({
          query,
          query_metadata: options.queryMetadata || null,
          model_config: options.modelConfig || this.defaultModel
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('RAG query error:', error);
      throw error;
    }
  }

  /**
   * Set default model configuration
   * @param {Object} modelConfig - Model configuration
   */
  async setDefaultModel(modelConfig) {
    try {
      const response = await fetch(`${this.baseUrl}/set_model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify(modelConfig)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Set model error:', error);
      throw error;
    }
  }

  /**
   * Get supported models
   * @returns {Promise<Object>} Supported models
   */
  async getSupportedModels() {
    try {
      const response = await fetch(`${this.baseUrl}/models`);
      return await response.json();
    } catch (error) {
      console.error('Get models error:', error);
      throw error;
    }
  }

  /**
   * Health check
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  /**
   * Query with Gemini
   * @param {string} query - The question
   * @param {Object} options - Query options
   */
  async queryWithGemini(query, options = {}) {
    return this.query(query, {
      ...options,
      modelConfig: {
        model_name: 'gemini-1.5-flash',
        api_key: process.env.NEXT_PUBLIC_GEMINI_API_KEY,
        max_tokens: 512,
        temperature: 0.7,
        ...options.modelConfig
      }
    });
  }

  /**
   * Query with OpenAI
   * @param {string} query - The question
   * @param {Object} options - Query options
   */
  async queryWithOpenAI(query, options = {}) {
    return this.query(query, {
      ...options,
      modelConfig: {
        model_name: 'gpt-3.5-turbo',
        api_key: process.env.NEXT_PUBLIC_OPENAI_API_KEY,
        max_tokens: 512,
        temperature: 0.7,
        ...options.modelConfig
      }
    });
  }

  /**
   * Query with HuggingFace (your fine-tuned model)
   * @param {string} query - The question
   * @param {string} modelName - Your fine-tuned model name
   * @param {Object} options - Query options
   */
  async queryWithHuggingFace(query, modelName, options = {}) {
    return this.query(query, {
      ...options,
      modelConfig: {
        model_name: modelName,
        api_key: process.env.NEXT_PUBLIC_HUGGINGFACE_API_KEY,
        max_tokens: 512,
        temperature: 0.7,
        ...options.modelConfig
      }
    });
  }
}

// React Hook for easy integration
export function useRAG(baseUrl = 'http://localhost:8080', apiKey = null) {
  const [client] = useState(() => new RAGClient(baseUrl, apiKey));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const query = async (question, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await client.query(question, options);
      setLoading(false);
      return result;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  return {
    client,
    query,
    loading,
    error,
    queryWithGemini: client.queryWithGemini.bind(client),
    queryWithOpenAI: client.queryWithOpenAI.bind(client),
    queryWithHuggingFace: client.queryWithHuggingFace.bind(client)
  };
}

export default RAGClient;
