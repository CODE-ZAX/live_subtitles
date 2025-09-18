import React, { useState, useEffect } from "react";
import { Toaster } from "react-hot-toast";
import Header from "./components/Header";
import VideoUpload from "./components/VideoUpload";
import StyleOptions from "./components/StyleOptions";
import ProcessingStatus from "./components/ProcessingStatus";
import useWebSocket from "./hooks/useWebSocket";
import {
  uploadVideo,
  getStatus,
  downloadVideo,
  downloadSubtitles,
  getStyles,
} from "./services/api";

function App() {
  const [currentStep, setCurrentStep] = useState("upload");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [processingStatus, setProcessingStatus] = useState(null);
  const [wsConnection, setWsConnection] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  const [styleOptions, setStyleOptions] = useState({
    font_size: 28,
    font_family: "Bangers-Regular.ttf",
    font_color: "white",
    highlight_color: "yellow",
    bottom_padding: 100,
    word_mode: true,
  });
  const [availableStyles, setAvailableStyles] = useState(null);

  useEffect(() => {
    // Load available style options
    loadStyleOptions();
  }, []);

  const loadStyleOptions = async () => {
    try {
      const styles = await getStyles();
      setAvailableStyles(styles);
    } catch (error) {
      console.error("Error loading style options:", error);
    }
  };

  const startPolling = (taskId) => {
    console.log("Starting polling for task:", taskId);
    const interval = setInterval(async () => {
      try {
        const status = await getStatus(taskId);
        console.log("Polling status update:", status);

        if (status.status === "completed" || status.status === "error") {
          console.log("Task completed via polling, stopping poller");
          clearInterval(interval);
          setPollingInterval(null);

          setProcessingStatus({
            status: status.status,
            progress: status.progress,
            message: status.message,
            step: status.step || 4,
            step_name: status.step_name || "Finalizing",
          });

          if (status.status === "completed") {
            setCurrentStep("completed");
          } else if (status.status === "error") {
            setCurrentStep("error");
          }
        } else {
          // Update progress from polling if WebSocket missed it
          setProcessingStatus((prev) => ({
            ...prev,
            status: status.status,
            progress: status.progress,
            message: status.message,
            step: status.step || prev?.step || 0,
            step_name: status.step_name || prev?.step_name || "Processing",
          }));
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 2000); // Poll every 2 seconds

    setPollingInterval(interval);
  };

  const stopPolling = () => {
    if (pollingInterval) {
      console.log("Stopping polling");
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  const handleFileUpload = async (file, styles) => {
    try {
      // Generate a temporary task ID for immediate WebSocket connection
      const tempTaskId = `temp_${Date.now()}_${Math.random()
        .toString(36)
        .substr(2, 9)}`;

      setCurrentStep("processing");
      setUploadedFile(file);
      setStyleOptions(styles);

      // Set initial processing status
      setProcessingStatus({
        status: "processing",
        progress: 0,
        message: "Starting upload...",
        step: 0,
        step_name: "Uploading",
      });

      // Establish WebSocket connection immediately
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsHost = window.location.host;
      const ws = new WebSocket(`${wsProtocol}//${wsHost}/ws/${tempTaskId}`);
      setWsConnection(ws);

      ws.onopen = () => {
        console.log("WebSocket connected for upload");
        setProcessingStatus((prev) => ({
          ...prev,
          message: "Connected, starting upload...",
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("WebSocket message received:", data);

          if (data.type === "progress") {
            console.log("Updating processing status with:", {
              status: data.status,
              progress: data.progress,
              message: data.message,
              step: data.step,
              step_name: data.step_name,
            });

            setProcessingStatus({
              status: data.status,
              progress: data.progress,
              message: data.message,
              step: data.step,
              step_name: data.step_name,
            });

            if (data.status === "completed") {
              setCurrentStep("completed");
              stopPolling(); // Stop polling since we got completion via WebSocket
            } else if (data.status === "error") {
              setCurrentStep("error");
              stopPolling(); // Stop polling since we got error via WebSocket
            }
          } else if (data.type === "connected") {
            console.log("WebSocket connection confirmed");
          } else if (data.type === "task_id_updated") {
            console.log("Task ID updated successfully:", data.new_task_id);
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
        setWsConnection(null);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      // Now start the upload
      const response = await uploadVideo(file, styles);

      // Update to real task ID
      setTaskId(response.task_id);

      // Send task ID update to WebSocket
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(
          JSON.stringify({
            type: "update_task_id",
            new_task_id: response.task_id,
          })
        );
      }

      // Start polling as a fallback
      startPolling(response.task_id);

      setProcessingStatus({
        status: "processing",
        progress: 0,
        message: "Starting transcription...",
        step: 0,
        step_name: "Initializing",
      });
    } catch (error) {
      console.error("Upload error:", error);
      setCurrentStep("error");
      stopPolling();
      if (wsConnection) {
        wsConnection.close();
        setWsConnection(null);
      }
    }
  };

  const handleDownloadVideo = async () => {
    if (taskId) {
      try {
        await downloadVideo(taskId);
      } catch (error) {
        console.error("Download error:", error);
      }
    }
  };

  const handleDownloadSubtitles = async () => {
    if (taskId) {
      try {
        await downloadSubtitles(taskId);
      } catch (error) {
        console.error("Download error:", error);
      }
    }
  };

  const handleReset = () => {
    setCurrentStep("upload");
    setUploadedFile(null);
    setTaskId(null);
    setProcessingStatus(null);

    // Stop polling
    stopPolling();

    // Close WebSocket connection
    if (wsConnection) {
      wsConnection.close();
      setWsConnection(null);
    }
  };

  // Cleanup WebSocket and polling on unmount
  useEffect(() => {
    return () => {
      stopPolling();
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, [wsConnection]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#1e293b",
            color: "#f1f5f9",
          },
        }}
      />

      <Header />

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {currentStep === "upload" && (
            <div className="space-y-8">
              <VideoUpload
                onFileUpload={handleFileUpload}
                availableStyles={availableStyles}
                styleOptions={styleOptions}
              />
              {availableStyles && (
                <StyleOptions
                  styles={styleOptions}
                  availableStyles={availableStyles}
                  onChange={setStyleOptions}
                />
              )}
            </div>
          )}

          {currentStep === "processing" && processingStatus && (
            <ProcessingStatus
              status={processingStatus}
              fileName={uploadedFile?.name}
            />
          )}

          {currentStep === "completed" && (
            <div className="text-center space-y-6">
              <div className="card max-w-md mx-auto">
                <div className="text-6xl mb-4">🎉</div>
                <h2 className="text-2xl font-bold text-gradient mb-4">
                  Processing Complete!
                </h2>
                <p className="text-slate-600 dark:text-slate-400 mb-6">
                  Your video has been successfully processed with subtitles.
                </p>
                <div className="space-y-3">
                  <button
                    onClick={handleDownloadVideo}
                    className="btn-primary w-full"
                  >
                    📥 Download Video with Subtitles
                  </button>
                  <button
                    onClick={handleDownloadSubtitles}
                    className="btn-secondary w-full"
                  >
                    📄 Download SRT File
                  </button>
                  <button
                    onClick={handleReset}
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Process Another Video
                  </button>
                </div>
              </div>
            </div>
          )}

          {currentStep === "error" && (
            <div className="text-center space-y-6">
              <div className="card max-w-md mx-auto">
                <div className="text-6xl mb-4">❌</div>
                <h2 className="text-2xl font-bold text-red-600 mb-4">
                  Processing Failed
                </h2>
                <p className="text-slate-600 dark:text-slate-400 mb-6">
                  There was an error processing your video. Please try again.
                </p>
                <button onClick={handleReset} className="btn-primary w-full">
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
