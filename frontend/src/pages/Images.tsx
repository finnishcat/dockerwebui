// pages/Images.tsx
import React, { useEffect, useState } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Images = () => {
  const [images, setImages] = useState([]);
  const [newImage, setNewImage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchImages = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/docker/images/local`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Error loading images");
      const data = await res.json();
      setImages(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handlePull = async () => {
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/docker/image/pull/local`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ image: newImage })
      });
      if (!res.ok) throw new Error("Error pulling image");
      setNewImage("");
      fetchImages();
    } catch (err: any) {
      setError(err.message || "Unknown error");
    }
  };

  const handleRemove = async (id: string) => {
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/docker/image/remove/local/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Error removing image");
      fetchImages();
    } catch (err: any) {
      setError(err.message || "Unknown error");
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Docker Images</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      <div className="flex mb-6 space-x-2">
        <input
          type="text"
          className="p-2 border rounded w-full"
          placeholder="e.g. nginx:latest"
          value={newImage}
          onChange={(e) => setNewImage(e.target.value)}
        />
        <button className="bg-blue-600 text-white px-4 rounded" onClick={handlePull}>
          Pull
        </button>
      </div>

      {loading ? (
        <div className="text-center py-10">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {images.map((img: any, index: number) => (
            <div key={index} className="bg-white p-4 rounded shadow relative">
              <h2 className="text-md font-bold truncate">
                {img.repo_tags?.[0] || "(none)"}
              </h2>
              <p className="text-sm text-gray-600">Size: {(img.size / 1024 / 1024).toFixed(2)} MB</p>
              <button
                className="absolute top-2 right-2 text-red-600 hover:text-red-800 text-sm"
                onClick={() => handleRemove(img.id)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Images;
