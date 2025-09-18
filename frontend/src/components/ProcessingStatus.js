import React from "react";
import { Loader2, CheckCircle, AlertCircle, Clock } from "lucide-react";

const ProcessingStatus = ({ status, fileName }) => {
  console.log("ProcessingStatus received status:", status);

  const getStatusIcon = () => {
    switch (status.status) {
      case "completed":
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      case "error":
        return <AlertCircle className="h-8 w-8 text-red-500" />;
      default:
        return <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case "completed":
        return "text-green-600 dark:text-green-400";
      case "error":
        return "text-red-600 dark:text-red-400";
      default:
        return "text-primary-600 dark:text-primary-400";
    }
  };

  const getProgressSteps = () => {
    const steps = [
      {
        name: "Transcribing Audio",
        completed: status.step >= 1,
        current: status.step === 1,
      },
      {
        name: "Generating Subtitles",
        completed: status.step >= 2,
        current: status.step === 2,
      },
      {
        name: "Creating Video",
        completed: status.step >= 3,
        current: status.step === 3,
      },
      {
        name: "Finalizing",
        completed: status.step >= 4,
        current: status.step === 4,
      },
    ];
    return steps;
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <div className="flex justify-center mb-4">{getStatusIcon()}</div>
        <h2 className={`text-2xl font-bold ${getStatusColor()}`}>
          {status.status === "completed"
            ? "Processing Complete!"
            : status.status === "error"
            ? "Processing Failed"
            : "Processing Your Video"}
        </h2>
        <p className="text-slate-600 dark:text-slate-400 mt-2">
          {fileName && `Processing: ${fileName}`}
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-slate-600 dark:text-slate-400 mb-2">
          <span>Progress</span>
          <span>{status.progress}%</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${status.progress}%` }}
          />
        </div>
      </div>

      {/* Status Message */}
      <div className="text-center mb-6">
        <p className="text-slate-700 dark:text-slate-300">{status.message}</p>
      </div>

      {/* Progress Steps */}
      <div className="space-y-3">
        {getProgressSteps().map((step, index) => (
          <div key={index} className="flex items-center space-x-3">
            <div
              className={`
                w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold
                ${
                  step.completed
                    ? "bg-green-500 text-white"
                    : step.current
                    ? "bg-primary-500 text-white animate-pulse"
                    : "bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400"
                }
              `}
            >
              {step.completed ? "✓" : index + 1}
            </div>
            <span
              className={`
                text-sm font-medium
                ${
                  step.completed
                    ? "text-green-600 dark:text-green-400"
                    : step.current
                    ? "text-primary-600 dark:text-primary-400 font-semibold"
                    : "text-slate-600 dark:text-slate-400"
                }
              `}
            >
              {step.name}
              {step.current && " (Current)"}
            </span>
            {step.completed && (
              <CheckCircle className="h-4 w-4 text-green-500 ml-auto" />
            )}
          </div>
        ))}
      </div>

      {/* Processing Time Estimate */}
      {status.status === "processing" && (
        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
          <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
            <Clock className="h-4 w-4" />
            <span>
              Processing time varies based on video length.
              {status.progress < 20 && " Audio transcription in progress..."}
              {status.progress >= 20 &&
                status.progress < 50 &&
                " Generating subtitles..."}
              {status.progress >= 50 &&
                status.progress < 80 &&
                " Creating video with subtitles..."}
              {status.progress >= 80 && " Almost done..."}
            </span>
          </div>
        </div>
      )}

      {/* Error Details */}
      {status.status === "error" && (
        <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800 dark:text-red-200">
                Processing Error
              </p>
              <p className="text-sm text-red-600 dark:text-red-400 mt-1">
                {status.message}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;
