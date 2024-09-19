"use client"; // Ensures that this file is treated as a client-side component

import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Home() {
  // State to store articles fetched from the database
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);  // Loading state
  const [error, setError] = useState(null);      // Error state

  // useEffect hook to fetch articles when the component mounts
  useEffect(() => {
    fetchArticles();
  }, []);

  // Function to fetch articles from the API
  const fetchArticles = async () => {
    setLoading(true);  // Set loading to true before starting fetch
    setError(null);    // Clear previous errors
    try {
      const res = await axios.get('/api/articles');
      setArticles(res.data);
    } catch (err) {
      setError('Failed to fetch articles. Please try again.');
    } finally {
      setLoading(false);  // Set loading to false after fetch completes
    }
  };

  // Optimistic deletion: Remove article from UI immediately
  const deleteArticle = async (id) => {
    const updatedArticles = articles.filter(article => article.id !== id);
    setArticles(updatedArticles);  // Optimistically update UI
    try {
      await axios.delete(`/api/articles?id=${id}`);
    } catch (err) {
      setError('Failed to delete the article. Please try again.');
      fetchArticles();  // Refetch in case of failure
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-6 text-center text-gray-800">BBC News Articles</h1>
      <div className="bg-white shadow-md rounded-lg p-6">
        {/* Display a loading spinner if the articles are still loading */}
        {loading ? (
          <div className="text-center">
            <svg className="animate-spin h-10 w-10 text-gray-500 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            <p className="text-gray-500 mt-2">Loading articles...</p>
          </div>
        ) : error ? (
          <p className="text-center bg-red-100 text-red-600 border border-red-300 p-4 rounded">{error}</p>
        ) : articles.length > 0 ? (
          <ul className="space-y-4">
            {articles.map((article) => (
              <li key={article.id} className="flex justify-between items-center p-6 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 ease-in-out">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-indigo-600 hover:text-indigo-800">{article.headline}</h2>
                    <a href={article.url} className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">
                      Read more
                    </a>
                  </div>
                </div>
                <button
                  onClick={() => deleteArticle(article.id)}
                  className="bg-red-500 text-white px-4 py-2 rounded-full shadow hover:bg-red-600 hover:shadow-lg transition duration-300"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-center text-gray-600">No articles found.</p>
        )}
      </div>
    </div>
  );
}
