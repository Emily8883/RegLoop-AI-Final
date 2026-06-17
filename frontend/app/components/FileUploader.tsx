"use client";

import { useState, useRef } from "react";
import { apiClient } from "@/services/api";

interface FileUploaderProps {
  onUploadSuccess?: (documentId: number, filename: string) => void;
  onUploadError?: (error: string) => void;
}

export function FileUploader({ onUploadSuccess, onUploadError }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [uploadMessage, setUploadMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): { valid: boolean; error?: string } => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ["application/pdf"];

    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: "Only PDF files are supported" };
    }

    if (file.size > maxSize) {
      return { valid: false, error: "File size must be less than 10MB" };
    }

    return { valid: true };
  };

  const handleUploadFile = async (file: File) => {
    const validation = validateFile(file);
    if (!validation.valid) {
      setUploadStatus("error");
      setUploadMessage(validation.error || "Invalid file");
      onUploadError?.(validation.error || "Invalid file");
      return;
    }

    setIsUploading(true);
    setUploadStatus("loading");
    setUploadProgress(0);
    setUploadMessage("Uploading...");

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + Math.random() * 30, 90));
      }, 200);

      const response = await apiClient.uploadFile(file);

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.error) {
        setUploadStatus("error");
        setUploadMessage(response.error || "Upload failed");
        onUploadError?.(response.error || "Upload failed");
      } else {
        setUploadStatus("success");
        setUploadMessage(`✓ Successfully uploaded: ${file.name}`);
        onUploadSuccess?.(response.data.document_id, file.name);

        // Reset after 2 seconds
        setTimeout(() => {
          setUploadStatus("idle");
          setUploadProgress(0);
          setUploadMessage("");
        }, 2000);
      }
    } catch (error) {
      setUploadStatus("error");
      const errorMsg = error instanceof Error ? error.message : "Upload failed";
      setUploadMessage(errorMsg);
      onUploadError?.(errorMsg);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleUploadFile(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files;
    if (files && files.length > 0) {
      handleUploadFile(files[0]);
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full space-y-4">
      {/* Upload Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClickUpload}
        className={`
          relative rounded-xl border-2 border-dashed transition-all duration-200 cursor-pointer
          ${isDragging || isUploading
            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
            : "border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-800/50"
          }
          ${uploadStatus === "success" ? "border-green-500 bg-green-50 dark:bg-green-900/20" : ""}
          ${uploadStatus === "error" ? "border-red-500 bg-red-50 dark:bg-red-900/20" : ""}
          hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20
          p-8
        `}
        role="button"
        tabIndex={0}
        aria-label="Drop zone for uploading PDF files"
        aria-describedby="upload-description"
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleClickUpload();
          }
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileInputChange}
          disabled={isUploading}
          className="hidden"
          aria-label="Upload PDF file"
        />

        <div className="flex flex-col items-center justify-center space-y-3 text-center">
          {uploadStatus === "loading" ? (
            <>
              <div className="text-4xl animate-pulse">📤</div>
              <div className="space-y-2">
                <p className="text-sm font-semibold text-slate-900 dark:text-white">Uploading...</p>
                <div className="w-48 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                    role="progressbar"
                    aria-valuenow={Math.round(uploadProgress)}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`Upload progress: ${Math.round(uploadProgress)}%`}
                  />
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400" aria-live="polite">
                  {Math.round(uploadProgress)}%
                </p>
              </div>
            </>
          ) : uploadStatus === "success" ? (
            <>
              <div className="text-4xl animate-scaleIn">✅</div>
              <p className="text-sm font-semibold text-green-700 dark:text-green-300" aria-live="polite">
                {uploadMessage}
              </p>
            </>
          ) : uploadStatus === "error" ? (
            <>
              <div className="text-4xl">❌</div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-red-700 dark:text-red-300">Upload Failed</p>
                <p className="text-xs text-red-600 dark:text-red-400" aria-live="polite">
                  {uploadMessage}
                </p>
              </div>
            </>
          ) : (
            <>
              <div className="text-4xl animate-slideInUp">📄</div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-slate-900 dark:text-white">
                  {isDragging ? "Drop your PDF here" : "Drag PDF here or click to upload"}
                </p>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  PDF files up to 10MB
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Upload Info */}
      {!isUploading && uploadStatus === "idle" && (
        <div
          className="rounded-lg border border-blue-200/50 dark:border-blue-800/50 bg-blue-50/50 dark:bg-blue-900/20 p-4"
          id="upload-description"
        >
          <p className="text-xs text-blue-700 dark:text-blue-300">
            <span className="font-semibold">💡 Tip:</span> Upload a PDF document to extract regulatory obligations automatically with AI-powered analysis.
          </p>
        </div>
      )}
    </div>
  );
}
