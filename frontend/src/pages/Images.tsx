import React, { useEffect, useState, useRef } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Images = () => {
  const [images, setImages] = useState([]);
  const [newImage, setNewImage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importMsg, setImportMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    if (!newImage.trim()) return;
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

  const handleExport = async (imageId: string, tag: string) => {
    setError(null);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/docker/image/save/local/${imageId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Error exporting image");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = tag.replace(/[:\/@]/g, "_") || imageId.replace(/[:\/@]/g, "_");
      a.download = `${safeName}.tar`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setImportMsg(null);
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const token = localStorage.getItem("token");
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_URL}/docker/image/load/local`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      if (!res.ok) throw new Error("Error importing image");
      const data = await res.json();
      setImportMsg(data.msg || "Image imported successfully");
      fetchImages();
    } catch (err: any) {
      setError(err.message || "Unknown error");
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
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
      {importMsg && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">{importMsg}</div>
      )}

      <div className="flex mb-6 space-x-2">
        <input
          type="text"
          className="p-2 border rounded w-full"
          placeholder="e.g. nginx:latest"
          value={newImage}
          onChange={(e) => setNewImage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handlePull()}
        />
        <button className="bg-blue-600 text-white px-4 rounded" onClick={handlePull}>
          Pull
        </button>
      </div>

      <div className="mb-6">
        <label className="bg-green-600 text-white px-4 py-2 rounded cursor-pointer inline-block hover:bg-green-700">
          Import Image (.tar)
          <input
            ref={fileInputRef}
            type="file"
            accept=".tar,.tar.gz"
            className="hidden"
            onChange={handleImport}
          />
        </label>
        <span className="ml-2 text-gray-500 text-sm">Upload a Docker image tar archive</span>
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
              <p className="text-xs text-gray-400 truncate">{img.id}</p>
              <div className="mt-2 flex space-x-2">
                <button
                  className="bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600"
                  onClick={() => handleExport(img.id, img.repo_tags?.[0] || img.id)}
                >
                  Export
                </button>
                <button
                  className="bg-red-600 text-white px-2 py-1 rounded text-xs hover:bg-red-700"
                  onClick={() => handleRemove(img.id)}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Images;
