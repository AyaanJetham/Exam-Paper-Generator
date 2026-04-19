import React, { useState } from "react";

const SetQuestionPaper: React.FC = () => {
  const [questionPapers, setQuestionPapers] = useState<File[]>([]);
  const [syllabusFile, setSyllabusFile] = useState<File | null>(null);
  const [threshold, setThreshold] = useState<number>(() => {
    const saved = localStorage.getItem("threshold");
    return saved ? Number(saved) : 30;
  });
  const [difficulty, setDifficulty] = useState<"easy" | "balanced" | "medium" | "hard">("medium");
  const [format, setFormat] = useState<"pdf" | "docx">("pdf");
  const [includeAnswers, setIncludeAnswers] = useState(false);
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
      alert("Please upload at least one question paper PDF.");
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
      formData.append("threshold", threshold.toString());
      formData.append("difficulty", difficulty);
      formData.append("file_format", format);
      formData.append("include_answers", includeAnswers.toString());

      localStorage.setItem("threshold", threshold.toString());

      const response = await fetch("http://localhost:8000/upload-question-paper", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to upload question papers");
      }

      const data = await response.json();
      console.log("Uploaded papers:", data);
      
      if (data.file_url) {
        setFileUrl(`http://localhost:8000${data.file_url}`);
      } else if (data.result && !data.result.success) {
        setErrorMsg(data.result.error || "Failed to generate question paper.");
      }
    } catch (error: any) {
      console.error("Error uploading question papers:", error);
      setErrorMsg(error.message || "Error generating question paper. Check backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-[24px] p-8 max-w-3xl mx-auto shadow-[0_1px_3px_rgba(0,0,0,0.12),0_1px_2px_rgba(0,0,0,0.24)] border border-[#e3e2e6] transition-all duration-300">
      
      <h2 className="text-2xl font-normal mb-8 text-[#1b1b1f]">
        Paper Generator
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Threshold */}
        <div>
          <label className="block text-sm font-medium text-[#444746] mb-3">
            Repetition Threshold (%)
          </label>
          <input
            type="number"
            min={0}
            max={100}
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="w-full border border-[#74777f] bg-white rounded-lg p-2.5 text-[#1b1b1f] outline-none focus:border-[#0b57d0] focus:ring-1 focus:ring-[#0b57d0]"
          />
        </div>

        {/* Difficulty Selector */}
        <div>
          <label className="block text-sm font-medium text-[#444746] mb-3">
            Difficulty Level
          </label>
          <div className="flex gap-2">
            {(["easy", "medium", "hard", "balanced"] as const).map((level) => (
              <button
                key={level}
                onClick={() => setDifficulty(level)}
                className={`flex-1 py-2 px-1 rounded-full text-xs font-medium transition-all duration-200 capitalize ${
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
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Include Answers Toggle */}
        <div>
          <label className="block text-sm font-medium text-[#444746] mb-3">
            Answer Key / Marking Scheme
          </label>
          <button
            onClick={() => setIncludeAnswers(!includeAnswers)}
            className={`w-full py-2.5 px-4 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-between border ${
              includeAnswers
                ? "bg-[#d3e3fd] text-[#041e49] border-[#0b57d0]"
                : "bg-white text-[#444746] border-[#74777f]"
            }`}
          >
            <span>Include Model Answers</span>
            <div className={`w-10 h-5 rounded-full relative transition-colors ${includeAnswers ? "bg-[#0b57d0]" : "bg-[#74777f]"}`}>
              <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${includeAnswers ? "left-5.5" : "left-0.5"}`}></div>
            </div>
          </button>
        </div>

        {/* Format Selector */}
        <div>
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
      </div>

      <div className="mb-8">
        <label className="block text-sm font-medium text-[#444746] mb-3 flex items-center justify-between">
          <span>Syllabus Reference (PDF)</span>
          <span className="text-[#444746] bg-[#e3e2e6] px-2 py-0.5 rounded text-[10px] font-medium tracking-wide border border-[#c4c7c5]">REQUIRED</span>
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
          Reference Papers (PDFs)
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
          className="bg-[#0b57d0] text-white font-medium text-sm py-3.5 px-8 rounded-full transition-all duration-200 hover:bg-[#0842a0] hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed w-full max-w-sm flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              Generating Paper...
            </>
          ) : (
            "Generate Question Paper"
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
                // Extract filename from URL path
                const fileName = fileUrl.split("/").pop() || `question_paper.${format}`;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
              } catch (err) {
                console.error("Download failed:", err);
              }
            }}
            className="bg-transparent text-[#0b57d0] hover:bg-[#d3e3fd] border border-[#0b57d0] font-medium text-sm py-3 px-8 rounded-full transition-all duration-200 block text-center w-full max-w-sm cursor-pointer"
          >
            Download {format.toUpperCase()} Document
          </button>
        )}

        {errorMsg && (
          <div className="bg-[#f9dedc] text-[#410e0b] p-4 text-sm w-full font-medium rounded-xl shadow-sm border border-[#f2b8b5]">
            {errorMsg}
          </div>
        )}
      </div>
    </div>
  );
};

export default SetQuestionPaper;

