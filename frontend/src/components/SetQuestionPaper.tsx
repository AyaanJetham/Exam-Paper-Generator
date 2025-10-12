import React, { useState } from "react";

const SetQuestionPaper: React.FC = () => {
  const [questionPapers, setQuestionPapers] = useState<File[]>([]);
  const [threshold, setThreshold] = useState<number>(() => {
    // load threshold if already saved before
    const saved = localStorage.getItem("threshold");
    return saved ? Number(saved) : 30;
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setQuestionPapers(newFiles);
    }
  };

  const handleCreate = async () => {
    if (questionPapers.length === 0) {
      alert("Please upload at least one question paper PDF.");
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      questionPapers.forEach((file) => formData.append("question_papers", file));
      formData.append("threshold", threshold.toString());

      //  Save locally for persistence
      localStorage.setItem("threshold", threshold.toString());

      // Send to backend (where you save in artifacts)
      const response = await fetch("http://localhost:8000/upload-question-paper", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Failed to upload question papers");

      const result = await response.json();
      console.log("Uploaded papers:", result);
      alert("Question papers and threshold stored successfully!");

      setQuestionPapers([]);
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = "";
    } catch (error) {
      console.error("Error uploading question papers:", error);
      alert("Error uploading question papers. Check backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-2xl shadow-lg max-w-3xl mx-auto mt-8">
      <h2 className="text-3xl font-bold mb-4 text-gray-800 text-center">
        Upload Question Papers
      </h2>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Repetition Threshold (%)
        </label>
        <input
          type="number"
          min={0}
          max={100}
          value={threshold}
          onChange={(e) => setThreshold(Number(e.target.value))}
          className="w-full border border-blue-200 bg-blue-50 focus:bg-blue-100 focus:border-blue-400 rounded-xl p-3 text-gray-800 text-center text-lg font-medium transition duration-200 outline-none"
        />
      </div>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Upload Question Papers (PDF)
        </label>
        <input
          type="file"
          multiple
          accept="application/pdf"
          onChange={handleFileChange}
          disabled={isLoading}
          className="block w-full text-sm text-gray-600 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer p-4"
        />
      </div>

      <div className="flex justify-center">
        <button
          onClick={handleCreate}
          disabled={questionPapers.length === 0 || isLoading}
          className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg transition duration-300"
        >
          {isLoading ? "Uploading..." : "Save & Upload"}
        </button>
      </div>
    </div>
  );
};

export default SetQuestionPaper;
