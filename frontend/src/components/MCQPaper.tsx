import React, { useState } from "react";

const MCQPaper: React.FC = () => {
  const [questionPapers, setQuestionPapers] = useState<File[]>([]);
  const [syllabusFile, setSyllabusFile] = useState<File | null>(null);
  const [difficulty, setDifficulty] = useState<"easy" | "balanced" | "medium" | "hard">("medium");
  const [format, setFormat] = useState<"pdf" | "docx">("pdf");
  const [isLoading, setIsLoading] = useState(false);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setQuestionPapers(Array.from(e.target.files));
    }
  };

  const handleSyllabusChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSyllabusFile(e.target.files[0]);
    }
  };

  const handleCreate = async () => {
    if (questionPapers.length === 0) {
      alert("Please upload at least one question paper PDF for reference.");
      return;
    }

    setIsLoading(true);
    setFileUrl(null);
    setErrorMsg(null);
    try {
      const formData = new FormData();
      questionPapers.forEach((file) => formData.append("question_papers", file));
      if (syllabusFile) {
        formData.append("syllabus_file", syllabusFile);
      }
      formData.append("difficulty", difficulty);
      formData.append("file_format", format);

      const response = await fetch("http://localhost:8000/generate-mcq", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Failed to generate MCQ paper");

      const data = await response.json();
      
      if (data.file_url) {
        setFileUrl(`http://localhost:8000${data.file_url}`);
      } else if (data.result && !data.result.success) {
        setErrorMsg(data.result.error || "Failed to generate MCQ paper.");
      }
    } catch (error) {
      console.error("Error generating MCQs:", error);
      setErrorMsg("Error generating MCQ paper. Check backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-[24px] p-8 max-w-3xl mx-auto shadow-[0_1px_3px_rgba(0,0,0,0.12),0_1px_2px_rgba(0,0,0,0.24)] border border-[#e3e2e6] transition-all duration-300">
      
      <h2 className="text-2xl font-normal mb-8 text-[#1b1b1f]">
        MCQ Paper Generator
      </h2>

      {/* Difficulty Selector */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-[#444746] mb-3">
          Difficulty Level
        </label>
        <div className="flex gap-2">
          {(["easy", "balanced", "medium", "hard"] as const).map((level) => (
            <button
              key={level}
              onClick={() => setDifficulty(level)}
              className={`flex-1 py-2 px-4 rounded-full text-sm font-medium transition-all duration-200 capitalize ${
                difficulty === level
                  ? "bg-[#0b57d0] text-white shadow-sm"
                  : "bg-[#f8f9fa] text-[#444746] hover:bg-[#e3e2e6]"
              }`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      {/* Format Selector */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-[#444746] mb-3">
          Output Format
        </label>
        <div className="flex gap-2">
          {(["pdf", "docx"] as const).map((fmt) => (
            <button
              key={fmt}
              onClick={() => setFormat(fmt)}
              className={`flex-1 py-2 px-4 rounded-full text-sm font-medium transition-all duration-200 uppercase ${
                format === fmt
                  ? "bg-[#0b57d0] text-white shadow-sm"
                  : "bg-[#f8f9fa] text-[#444746] hover:bg-[#e3e2e6]"
              }`}
            >
              {fmt}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-8">
        <label className="block text-sm font-medium text-[#444746] mb-3 flex items-center justify-between">
          <span>Syllabus Reference</span>
          <span className="text-[#444746] bg-[#e3e2e6] px-2 py-0.5 rounded text-[10px] font-medium tracking-wide border border-[#c4c7c5]">OPTIONAL</span>
        </label>
        <div className="relative">
          <input
            type="file"
            accept="application/pdf"
            onChange={handleSyllabusChange}
            disabled={isLoading}
            className="block w-full text-sm text-[#444746] file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-medium file:bg-[#d3e3fd] file:text-[#041e49] hover:file:bg-[#b0cbec] file:transition-colors cursor-pointer p-2 bg-[#f8f9fa] border border-[#74777f] rounded-lg focus:outline-none focus:border-[#0b57d0] focus:ring-1 focus:ring-[#0b57d0]"
          />
        </div>
      </div>

      <div className="mb-10">
        <label className="block text-sm font-medium text-[#444746] mb-3">
          Reference Papers for MCQs
        </label>
        <div className="relative">
          <input
            type="file"
            multiple
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={isLoading}
            className="block w-full text-sm text-[#444746] file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-medium file:bg-[#d3e3fd] file:text-[#041e49] hover:file:bg-[#b0cbec] file:transition-colors cursor-pointer p-2 bg-[#f8f9fa] border border-[#74777f] rounded-lg focus:outline-none focus:border-[#0b57d0] focus:ring-1 focus:ring-[#0b57d0]"
          />
        </div>
      </div>

      <div className="flex justify-center flex-col items-center gap-4">
        <button
          onClick={handleCreate}
          disabled={questionPapers.length === 0 || isLoading}
          className="bg-[#0b57d0] text-white font-medium text-sm py-3 px-8 rounded-full transition-all duration-200 hover:bg-[#0842a0] hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed w-full max-w-xs flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              Generating 40 MCQs...
            </>
          ) : (
            "Generate MCQ Document"
          )}
        </button>

        {fileUrl && (
          <button
            onClick={async () => {
              try {
                const res = await fetch(fileUrl);
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                const fileName = fileUrl.split("/").pop() || `mcq_paper.${format}`;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
              } catch (err) {
                console.error("Download failed:", err);
              }
            }}
            className="bg-transparent text-[#0b57d0] hover:bg-[#d3e3fd] border border-[#0b57d0] font-medium text-sm py-3 px-8 rounded-full transition-all duration-200 block text-center w-full max-w-xs cursor-pointer"
          >
            Download MCQ {format.toUpperCase()}
          </button>
        )}

        {errorMsg && (
          <div className="bg-[#f9dedc] text-[#410e0b] p-4 text-sm w-full font-medium rounded-xl shadow-sm border border-[#f2b8b5]">
            {errorMsg}
          </div>
        )}
      </div>
      <p className="mt-6 text-center text-xs text-[#444746]">
        80 Marks | 40 Questions | 2 Marks Each | Includes Answer Key
      </p>
    </div>
  );
};

export default MCQPaper;
