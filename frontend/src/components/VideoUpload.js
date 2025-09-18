import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileVideo, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";

const VideoUpload = ({ onFileUpload, availableStyles, styleOptions }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const error = rejectedFiles[0].errors[0];
      if (error.code === "file-too-large") {
        toast.error(
          "File is too large. Please select a file smaller than 100MB."
        );
      } else if (error.code === "file-invalid-type") {
        toast.error("Please select a valid video file (MP4, AVI, MOV, etc.).");
      } else {
        toast.error("Invalid file. Please try again.");
      }
      return;
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      toast.success(`Selected: ${file.name}`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragReject } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"],
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: false,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
  });

  const handleUpload = () => {
    if (!selectedFile) {
      toast.error("Please select a video file first.");
      return;
    }

    if (!availableStyles) {
      toast.error("Style options not loaded. Please try again.");
      return;
    }

    if (!styleOptions) {
      toast.error("Style options not configured. Please try again.");
      return;
    }

    console.log("Uploading with style options:", styleOptions);
    onFileUpload(selectedFile, styleOptions);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div className="card">
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 mb-4">
          📁 Upload Your Video
        </h2>

        <div
          {...getRootProps()}
          className={`
            relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
            ${
              isDragActive
                ? "border-primary-400 bg-primary-50 dark:bg-primary-900/20"
                : "border-slate-300 dark:border-slate-600 hover:border-primary-400 hover:bg-slate-50 dark:hover:bg-slate-700/50"
            }
            ${isDragReject ? "border-red-400 bg-red-50 dark:bg-red-900/20" : ""}
          `}
        >
          <input {...getInputProps()} />

          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              {isDragReject ? (
                <AlertCircle className="h-8 w-8 text-red-500" />
              ) : (
                <Upload className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              )}
            </div>

            <div>
              <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {isDragReject
                  ? "Invalid file type"
                  : isDragActive
                  ? "Drop your video here"
                  : "Drag & drop your video here"}
              </p>
              <p className="text-slate-600 dark:text-slate-400 mt-1">
                or click to browse files
              </p>
            </div>

            <div className="text-sm text-slate-500 dark:text-slate-400">
              <p>Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM</p>
              <p>Maximum file size: 100MB</p>
            </div>
          </div>
        </div>

        {/* Selected File Info */}
        {selectedFile && (
          <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
            <div className="flex items-center space-x-3">
              <FileVideo className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                  {selectedFile.name}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Upload Button */}
        <div className="mt-6">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || !availableStyles}
            className={`
              w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200
              ${
                selectedFile && availableStyles
                  ? "btn-primary"
                  : "bg-slate-300 dark:bg-slate-600 text-slate-500 dark:text-slate-400 cursor-not-allowed"
              }
            `}
          >
            {!availableStyles ? "Loading..." : "🚀 Start Processing"}
          </button>
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="text-3xl mb-2">🎯</div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
            AI-Powered
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Advanced speech recognition with OpenAI Whisper
          </p>
        </div>

        <div className="card text-center">
          <div className="text-3xl mb-2">🎨</div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
            Customizable
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Full control over subtitle styling and appearance
          </p>
        </div>

        <div className="card text-center">
          <div className="text-3xl mb-2">⚡</div>
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">
            Fast Processing
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Quick transcription and subtitle generation
          </p>
        </div>
      </div>
    </div>
  );
};

export default VideoUpload;
